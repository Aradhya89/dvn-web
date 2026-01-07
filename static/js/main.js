// Simple scroll reveal using IntersectionObserver
document.addEventListener("DOMContentLoaded", () => {
  const revealEls = document.querySelectorAll(".reveal");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          // once visible, stop observing
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.15,
    }
  );

  revealEls.forEach((el) => observer.observe(el));
});

 const toggleBtn = document.getElementById("theme-toggle");

  // Check saved theme
  if (localStorage.getItem("theme") === "dark") {
      document.documentElement.classList.add("dark");
      toggleBtn.textContent = "☀️";
  }

  toggleBtn.addEventListener("click", () => {
      document.documentElement.classList.toggle("dark");

      if (document.documentElement.classList.contains("dark")) {
          localStorage.setItem("theme", "dark");
          toggleBtn.textContent = "☀️";
      } else {
          localStorage.setItem("theme", "light");
          toggleBtn.textContent = "🌙";
      }
  });

// function validateForm() {
//   const name = document.querySelector('[name="name"]').value.trim();
//   const email = document.querySelector('[name="email"]').value.trim();
//   const message = document.querySelector('[name="message"]').value.trim();

//   if (!name || !email || !message) {
//     alert("Please fill all fields before submitting");
//     return false; // stop submit
//   }
//   return true; // allow submit
// }



window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  if (params.get("msg") === "success") {
    showToast("Message Sended Successfully!");
  }
});


function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000); // auto-hide after 3 sec
}


