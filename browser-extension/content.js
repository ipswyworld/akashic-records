// content.js - Enhanced with Targeting Mode
console.log("Akasha Sub-Agent Content Script Active.");

let isTargeting = false;
let hoverElement = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "start_targeting") {
    isTargeting = true;
    document.body.style.cursor = "crosshair";
    addHighlightListeners();
    sendResponse({ status: "targeting_started" });
  } else if (request.action === "stop_targeting") {
    stopTargeting();
    sendResponse({ status: "targeting_stopped" });
  }
});

function addHighlightListeners() {
  document.addEventListener("mouseover", onMouseOver);
  document.addEventListener("mouseout", onMouseOut);
  document.addEventListener("click", onClick, true);
}

function stopTargeting() {
  isTargeting = false;
  document.body.style.cursor = "default";
  document.removeEventListener("mouseover", onMouseOver);
  document.removeEventListener("mouseout", onMouseOut);
  document.removeEventListener("click", onClick, true);
  if (hoverElement) hoverElement.style.outline = "";
}

function onMouseOver(e) {
  if (!isTargeting) return;
  if (hoverElement) hoverElement.style.outline = "";
  hoverElement = e.target;
  hoverElement.style.outline = "2px solid #bb86fc";
}

function onMouseOut(e) {
  if (!isTargeting) return;
  e.target.style.outline = "";
}

function onClick(e) {
  if (!isTargeting) return;
  e.preventDefault();
  e.stopPropagation();

  const selector = getCssSelector(e.target);
  const text = e.target.innerText.trim();
  
  chrome.runtime.sendMessage({
    action: "element_targeted",
    selector: selector,
    text: text,
    url: window.location.href
  });

  stopTargeting();
}

function getCssSelector(el) {
  if (el.id) return `#${el.id}`;
  if (el === document.body) return "body";

  let path = [];
  while (el.parentNode) {
    let tag = el.tagName.toLowerCase();
    let siblings = Array.from(el.parentNode.children).filter(s => s.tagName === el.tagName);
    if (siblings.length > 1) {
      let index = siblings.indexOf(el) + 1;
      tag += `:nth-child(${index})`;
    }
    path.unshift(tag);
    el = el.parentNode;
  }
  return path.join(" > ");
}
