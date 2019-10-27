import React, { useState, useEffect } from "react";
import posed, { PoseGroup } from "react-pose";

function EnterExitAnimation({ children }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    setInterval(() => setVisible(true), 500);
    return () => setVisible(false);
  }, []);
  const Panel = posed.div({
    enter: {
      y: 0,
      opacity: 1,
      delay: 300,
      transition: {
        y: { type: "spring", stiffness: 1000, damping: 15 },
        default: { duration: 300 }
      }
    },
    exit: {
      y: 50,
      opacity: 0,
      transition: { duration: 150 }
    }
  });
  return (
    <PoseGroup>{visible && <Panel key="panel">{children}</Panel>}</PoseGroup>
  );
}

export { EnterExitAnimation };
