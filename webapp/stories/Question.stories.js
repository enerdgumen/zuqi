import React from "react";
import centered from "@storybook/addon-centered/react";
import { action } from "@storybook/addon-actions";
import { withKnobs, boolean } from "@storybook/addon-knobs";
import {
  QuestionPanel,
  ChallengeButton,
  QuestionAnswers,
  QuestionAnswer
} from "../src/Question";

export default {
  title: "Question",
  decorators: [centered, withKnobs]
};

export const WithChallenge = () => (
  <QuestionPanel question="What does the acronym CDN stand for in terms of networking?">
    <ChallengeButton
      onChallenge={action("Challenge")}
      enabled={boolean("Enabled", true)}
      challenging={boolean("Challenging", false)}
    />
  </QuestionPanel>
);

export const WithAnswers = () => (
  <QuestionPanel question="What does the acronym CDN stand for in terms of networking?">
    <QuestionAnswers>
      <QuestionAnswer
        index={0}
        text="Content Delivery Network"
        onSelect={action("Select")}
      />
      <QuestionAnswer
        index={1}
        text="Content Distribution Network"
        status="loading"
        onSelect={action("Select")}
      />
      <QuestionAnswer
        index={2}
        text="Computational Data Network"
        status="success"
        onSelect={action("Select")}
      />
      <QuestionAnswer
        index={3}
        text="Compressed Data Network"
        status="failure"
        onSelect={action("Select")}
      />
    </QuestionAnswers>
  </QuestionPanel>
);
