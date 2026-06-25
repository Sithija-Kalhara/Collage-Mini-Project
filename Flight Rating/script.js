const starGroups = document.querySelectorAll(".stars");

starGroups.forEach(group => {
  const stars = group.querySelectorAll("span");
  const result = group.parentElement.querySelector(".result");

  stars.forEach((star, index) => {
    star.addEventListener("click", () => {

      stars.forEach(s => s.classList.remove("active"));

      for (let i = 0; i <= index; i++) {
        stars[i].classList.add("active");
      }

      result.textContent = `You rated ${index + 1} out of 5 stars ⭐`;
    });
  });
});enderTable();