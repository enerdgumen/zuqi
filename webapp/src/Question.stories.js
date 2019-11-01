import React from "react";
import centered from "@storybook/addon-centered/react";
import { action } from "@storybook/addon-actions";
import { withKnobs, boolean } from "@storybook/addon-knobs";
import { QuestionPanel } from "./Question";

export default {
  title: "Question",
  decorators: [centered, withKnobs]
};

export const Panel = () => (
  <QuestionPanel
    question="What was the first commercially available computer processor?"
    onChallenge={action("Challenge")}
    challenging={boolean("Challenging", false)}
    disabled={boolean("Disabled", false)}
  />
);
