function emulateUsernameNotAvailable() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      reject(Error("usernameNotAvailable"));
    }, 1000);
  });
}

function enter(username) {
  return emulateUsernameNotAvailable();
}

export { enter };
