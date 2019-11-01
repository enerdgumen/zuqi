import React from "react";
import centered from "@storybook/addon-centered/react";
import { action } from "@storybook/addon-actions";
import {
  withKnobs,
  boolean,
  array,
  number,
  select
} from "@storybook/addon-knobs";

import { QuestionPanel, QuestionAnswers } from "./Question";

export default {
  title: "Question",
  decorators: [centered, withKnobs]
};

export const Panel = () => (
  <QuestionPanel
    question="What does the acronym CDN stand for in terms of networking?"
    onChallenge={action("Challenge")}
    challenging={boolean("Challenging", false)}
    disabled={boolean("Disabled", false)}
  />
);

export const Answers = () => (
  <QuestionAnswers
    answers={array("Answers", [
      "Content Delivery Network",
      "Content Distribution Network",
      "Computational Data Network",
      "Compressed Data Network"
    ])}
    selection={number("Selection", 1)}
    status={select("Status", ["loading", "success", "failure"], "success")}
    onSelect={action("Selected")}
  />
);
