import React from "react";
import centered from "@storybook/addon-centered/react";
import { action } from "@storybook/addon-actions";
import { withKnobs, boolean } from "@storybook/addon-knobs";
import { LoadingButton } from "../src/LoadingButton";

export default {
  title: "Button",
  decorators: [centered, withKnobs]
};

export const Loadable = () => (
  <LoadingButton
    variant="contained"
    color="primary"
    onClick={action("Click")}
    loading={boolean("Loading", false)}
    disabled={boolean("Disabled", false)}
  >
    Button
  </LoadingButton>
);
