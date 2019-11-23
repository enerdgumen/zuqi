export async function openSocket(username) {
  return new Promise((resolve, reject) => {
    const { protocol, hostname, port } = window.location;
    const proto = protocol === "https:" ? "wss:" : "ws:";
    const uid = encodeURIComponent(username);
    const socketPort = process.env.REACT_APP_SOCKET_PORT || port;
    const url = `${proto}//${hostname}:${socketPort}/play?uid=${uid}`;
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
          return reject(Error(data.reason));
        case "ready":
          return resolve(socket);
        default:
          console.log("unexpected message", data);
      }
    };
    socket.onerror = err => reject(err);
  });
}
