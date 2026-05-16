// Убедитесь, что элемент уже загружен (с defer это гарантировано)
const contactModal = document.getElementById("contactModal");
contactModal.addEventListener("click", (e) => {
  if (e.target === contactModal) {
    contactModal.close();
  }
});

const contactButton = document.querySelector(".contact__card-button");
contactButton.addEventListener("click", () => {
  if (contactModal) {
    console.log("click");
    contactModal.showModal();
  }
});

const dismissBtn = document.getElementById("dismiss");
dismissBtn.addEventListener("click", () => {
  contactModal.close();
});

const feedbackForm = document.getElementById("feedbackForm");
feedbackForm.addEventListener("keypress", function (event) {
  if (event.key === "Enter" && event.target.type !== "textarea") {
    event.preventDefault();
  }
});

// Функция для отправки формы
function submitForm() {
  const formData = new FormData(feedbackForm);

  if (!feedbackForm.checkValidity()) {
    feedbackForm.reportValidity();
    return;
  }

  const data = {
    name: formData.get("name"),
    phone: formData.get("phone"),
    email: formData.get("email"),
    category: formData.get("category"),
    message: formData.get("message"),
  };

  console.log("Данные формы:", data);
  alert(
    "Спасибо! Ваше обращение отправлено. Мы свяжемся с вами в ближайшее время."
  );
  contactModal.close();
  feedbackForm.reset();
}

const submitBtn = document.querySelector("button[type='submit']");
submitBtn.addEventListener("click", () => {
  submitForm();
});
