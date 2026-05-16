const body = document.querySelector("body");

const darkModeBtn = document.getElementById("button__dark-mode");

let theme = localStorage.getItem("theme");
setTheme(theme, darkModeBtn);

function setDark(darkModeBtn) {
  body.classList.add("dark");
  darkModeBtn.classList.add("active");
  localStorage.setItem("theme", "dark");
  theme = "dark";
}

function setLight(darkModeBtn) {
  body.classList.remove("dark");
  darkModeBtn.classList.remove("active");
  localStorage.setItem("theme", "light");
  theme = "light";
}

function setTheme(theme, darkModeBtn) {
  if (theme !== null && theme !== undefined) {
    if (theme === "light") {
      setLight(darkModeBtn);
    } else {
      setDark(darkModeBtn);
    }
  } else {
    setLight(darkModeBtn);
  }
}

function getOppositeTheme(theme) {
  return theme === "light" ? "dark" : "light";
}

darkModeBtn.addEventListener("click", () => {
  const oppositeTheme = getOppositeTheme(theme);
  setTheme(oppositeTheme, darkModeBtn);
});
