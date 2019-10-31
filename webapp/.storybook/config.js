import React from "react";
import { configure, addDecorator } from "@storybook/react";
import { SnackbarProvider } from "../src/Snackbar";
import { Theme } from "../src/Theme";
import '../src/i18n';

addDecorator(storyFn => (
  <Theme>
    <SnackbarProvider>{storyFn()}</SnackbarProvider>
  </Theme>
));

configure(require.context("../src", true, /\.stories\.js$/), module);
