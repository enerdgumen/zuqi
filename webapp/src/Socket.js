export async function openSocket(username) {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(
      `ws://localhost:8000/?uid=${encodeURIComponent(username)}`
    );
    socket.sendJson = data => {
      console.log("send", data);
      setTimeout(() => socket.send(JSON.stringify(data)), 1000);
    };
    socket.onopen = () => {
      resolve(socket);
    };
    socket.onerror = err => reject(err);
  });
}
