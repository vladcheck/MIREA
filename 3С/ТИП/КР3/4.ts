// 12. Напишите timeout(promise, ms), которая возвращает промис,
// отклоняющийся, если исходный promise не выполнен за ms миллисекунд.
// Примените это к fetch().

function timeout(promise, ms, message = "Timeout") {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(message));
      }, ms);
    }),
  ]);
}

async function fetchDataWithTimeout(url, timeoutMs = 5000) {
  try {
    const response = await timeout(
      fetch(url),
      timeoutMs,
      `Запрос к ${url} превысил время ожидания ${timeoutMs}мс`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    } else {
      return response;
    }
  } catch (error) {
    console.error("Ошибка при выполнении запроса:", error);
    throw error;
  }
}

function main() {
  fetchDataWithTimeout(
    "https://dev.to/asimkhan0/how-to-stop-a-pending-promise-in-javascript-timing-based-rejection-1bn5",
    5
  )
    .then((res) => {
      console.log(res);
    })
    .catch((e) => {
      console.log(e);
    });
}

main();
