import React from "react";
import centered from "@storybook/addon-centered/react";
import { action } from "@storybook/addon-actions";
import { withKnobs, boolean } from "@storybook/addon-knobs";
import { Welcome } from "../src/Welcome";

export default {
  title: "Welcome",
  decorators: [centered, withKnobs]
};

export const Panel = () => (
  <Welcome
    onEnter={action("Enter")}
    entering={boolean("Loading", false)}
  />
);
