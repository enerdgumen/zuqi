import { useState } from "react";

export function useMonitor(asyncHandler) {
  const [loading, setLoading] = useState(false);
  const callback = async (...args) => {
    setLoading(true);
    try {
      await asyncHandler(...args);
    } finally {
      setLoading(false);
    }
  };
  return [loading, callback];
}