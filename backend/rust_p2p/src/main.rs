use libp2p::{
    futures::StreamExt,
    gossipsub, mdns, noise,
    swarm::{NetworkBehaviour, SwarmEvent},
    tcp, yamux,
};
use std::error::Error;
use std::time::Duration;
use tokio::{io, io::AsyncBufReadExt, select};
use serde::{Deserialize, Serialize};
use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce
};
use pbkdf2::pbkdf2;
use pbkdf2::hmac::Hmac;
use sha2::Sha256;
use base64::{Engine as _, engine::general_purpose};

#[derive(NetworkBehaviour)]
struct AkashaBehaviour {
    gossipsub: gossipsub::Behaviour,
    mdns: mdns::tokio::Behaviour,
}

#[derive(Serialize, Deserialize)]
struct IPCMessage {
    #[serde(rename = "type")]
    msg_type: String,
    payload: serde_json::Value,
}

struct EncryptionEngine {
    key: [u8; 32],
}

impl EncryptionEngine {
    fn new(password: &str, salt: &str) -> Self {
        let mut key = [0u8; 32];
        pbkdf2::<Hmac<Sha256>>(password.as_bytes(), salt.as_bytes(), 100_000, &mut key).expect("KDF failed");
        Self { key }
    }

    fn encrypt(&self, data: &str) -> String {
        let cipher = Aes256Gcm::new(&self.key.into());
        let nonce = Nonce::from_slice(b"unique nonce 12"); 
        let ciphertext = cipher.encrypt(nonce, data.as_bytes()).expect("Encryption failed");
        general_purpose::STANDARD.encode(ciphertext)
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let mut swarm = libp2p::SwarmBuilder::with_new_identity()
        .with_tokio()
        .with_tcp(
            tcp::Config::default(),
            noise::Config::new,
            yamux::Config::default,
        )?
        .with_behaviour(|key| {
            let gossipsub_config = gossipsub::ConfigBuilder::default()
                .heartbeat_interval(Duration::from_secs(10))
                .validation_mode(gossipsub::ValidationMode::Strict)
                .build()
                .map_err(|msg| std::io::Error::new(std::io::ErrorKind::Other, msg))?;
            
            let gossipsub = gossipsub::Behaviour::new(
                gossipsub::MessageAuthenticity::Signed(key.clone()),
                gossipsub_config,
            )?;
            
            let mdns = mdns::tokio::Behaviour::new(mdns::Config::default(), key.public().to_peer_id())?;
            
            Ok(AkashaBehaviour { gossipsub, mdns })
        })?
        .with_swarm_config(|c| c.with_idle_connection_timeout(Duration::from_secs(60)))
        .build();

    let topic = gossipsub::IdentTopic::new("akasha-sync");
    swarm.behaviour_mut().gossipsub.subscribe(&topic)?;

    swarm.listen_on("/ip4/0.0.0.0/tcp/0".parse()?)?;

    println!("Bifrost Rust Mesh: Node Initialized.");

    let mut stdin = io::BufReader::new(io::stdin()).lines();

    loop {
        select! {
            line_res = stdin.next_line() => {
                if let Ok(Some(line)) = line_res {
                    if let Ok(msg) = serde_json::from_str::<IPCMessage>(&line) {
                        if msg.msg_type == "ENCRYPT_BACKUP" {
                            let pass = msg.payload["password"].as_str().unwrap_or("default");
                            let data = msg.payload["data"].as_str().unwrap_or("");
                            let engine = EncryptionEngine::new(pass, "akasha_salt");
                            let encrypted = engine.encrypt(data);
                            println!("ZKP_BACKUP_RESULT:{}", encrypted);
                        }
                    }
                }
            },
            event = swarm.select_next_some() => match event {
                SwarmEvent::Behaviour(AkashaBehaviourEvent::Mdns(mdns::Event::Discovered(list))) => {
                    for (peer_id, _multiaddr) in list {
                        swarm.behaviour_mut().gossipsub.add_explicit_peer(&peer_id);
                    }
                },
                _ => {}
            }
        }
    }
}
