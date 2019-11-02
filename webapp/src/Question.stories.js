import React from "react";
import centered from "@storybook/addon-centered/react";
import { action } from "@storybook/addon-actions";
import { withKnobs, boolean, object } from "@storybook/addon-knobs";
import { QuestionPanel, ChallengeButton, QuestionAnswers } from "./Question";

export default {
  title: "Question",
  decorators: [centered, withKnobs]
};

export const WithChallenge = () => (
  <QuestionPanel question="What does the acronym CDN stand for in terms of networking?">
    <ChallengeButton
      onChallenge={action("Challenge")}
      challenging={boolean("Challenging", false)}
      disabled={boolean("Disabled", false)}
    />
  </QuestionPanel>
);

export const WithAnswers = () => (
  <QuestionPanel question="What does the acronym CDN stand for in terms of networking?">
    <QuestionAnswers
      onSelect={action("Select")}
      answers={object("Answers", [
        {
          text: "Content Delivery Network"
        },
        {
          text: "Content Distribution Network",
          status: "loading"
        },
        {
          text: "Computational Data Network",
          status: "success"
        },
        {
          text: "Compressed Data Network",
          status: "failure"
        }
      ])}
    />
  </QuestionPanel>
);
