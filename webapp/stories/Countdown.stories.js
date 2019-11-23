import React from "react";
import { withKnobs, number } from "@storybook/addon-knobs";
import { Countdown } from "../src/Countdown";

export default {
  title: "Countdown",
  decorators: [withKnobs]
};

export const Controlled = () => (
  <Countdown total={number("Total", 5)} current={number("Current", 3)} />
);
