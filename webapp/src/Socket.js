export async function openSocket(username) {
  return new Promise((resolve, reject) => {
    const hostname = window.location.hostname;
    const url = `ws://${hostname}:8000/play?uid=${encodeURIComponent(username)}`;
    const socket = new WebSocket(url);
    socket.sendJson = data => {
      console.log("send", data);
      socket.send(JSON.stringify(data));
    };
    socket.onmessage = message => {
      const data = JSON.parse(message.data);
      console.log("message:", data);
      switch (data.event) {
        case "rejected":
          return reject(Error("usernameNotAvailable"));
        case "ready":
          return resolve(socket);
        default:
          console.log("unexpected message", data);
      }
    };
    socket.onerror = err => reject(err);
  });
}
