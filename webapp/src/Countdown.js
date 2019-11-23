import React, { useEffect, useState } from "react";
import Box from "@material-ui/core/Box";
import LinearProgress from "@material-ui/core/LinearProgress";
import ScheduleIcon from "@material-ui/icons/Schedule";

export function Countdown({ total, current }) {
  const color = current > 0 ? "primary" : "secondary";
  return (
    <Box
      display="flex"
      position="absolute"
      bottom="1em"
      flexDirection="row"
      alignItems="center"
      width="40vw"
      ml={1}
      mt={2}
      mr={1}
    >
      <ScheduleIcon color={color} />
      <Box flexGrow={1} ml={1}>
        <LinearProgress
          color={color}
          variant="determinate"
          value={(100 * current) / total}
        />
      </Box>
    </Box>
  );
}

export function useCountdown(seconds) {
  const [countdown, setCountdown] = useState(seconds);
  const [timer, setTimer] = useState();
  const start = () => {
    const interval = setInterval(() => {
      setCountdown(it => it - 1);
    }, 1000);
    setTimer(interval);
  };
  const stop = () => {
    clearInterval(timer);
  };
  useEffect(() => {
    start();
    return stop;
  }, []);
  useEffect(() => {
    if (countdown === 0) stop();
  }, [countdown]);
  return countdown;
}
