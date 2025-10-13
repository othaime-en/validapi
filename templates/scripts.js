function showTab(tabName) {
  // Hide all tab contents
  const contents = document.querySelectorAll(".tab-content");
  contents.forEach((content) => content.classList.remove("active"));

  // Remove active class from all tabs
  const tabs = document.querySelectorAll(".tab");
  tabs.forEach((tab) => tab.classList.remove("active"));

  // Show selected tab content
  document.getElementById(tabName).classList.add("active");

  // Add active class to clicked tab
  event.target.classList.add("active");
}

function toggleCollapsible(element) {
  element.classList.toggle("active");
  const content = element.nextElementSibling;
  content.classList.toggle("show");
}

// Add click handlers to all collapsibles
document.addEventListener("DOMContentLoaded", function () {
  const collapsibles = document.querySelectorAll(".collapsible");
  collapsibles.forEach(function (collapsible) {
    collapsible.addEventListener("click", function () {
      toggleCollapsible(this);
    });
  });
});
