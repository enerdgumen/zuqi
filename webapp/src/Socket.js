export async function openSocket(username) {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(
      `ws://localhost:8000/?uid=${encodeURIComponent(username)}`
    );
    socket.sendJson = data => {
      console.log("send", data);
      setTimeout(() => socket.send(JSON.stringify(data)), 1000);
    };
    socket.onmessage = message => {
      const data = JSON.parse(message.data);
      console.log("message:", data);
      switch (data.event) {
        case "rejected":
          return reject(Error('usernameNotAvailable'));
        case "ready":
          return resolve(socket);
        default:
          console.log("unexpected message", data);
      }
    };
    socket.onerror = err => reject(err);
  });
}
