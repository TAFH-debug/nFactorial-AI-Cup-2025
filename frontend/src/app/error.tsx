"use client";

import { Button } from "@heroui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <div>{error.message}</div>
      <Button onPress={() => reset()}>Try again</Button>
    </div>
  );
}
