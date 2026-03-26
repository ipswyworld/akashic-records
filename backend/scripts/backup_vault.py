import shutil
import os
import datetime
import tarfile

def backup_vault():
    vault_path = "akasha_data/sovereign_vault"
    backup_dir = "akasha_data/redundancy/backups"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"vault_backup_{timestamp}.tar.gz")
    
    print(f"Starting backup of {vault_path} to {backup_file}...")
    
    try:
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(vault_path, arcname=os.path.basename(vault_path))
        print("Backup successful.")
        
        # Prune old backups (keep last 5)
        backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".tar.gz")])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(old_backup)
                print(f"Pruned old backup: {old_backup}")
                
    except Exception as e:
        print(f"Backup failed: {e}")

if __name__ == "__main__":
    backup_vault()
