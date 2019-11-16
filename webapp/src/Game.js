import React, { useState, Fragment } from "react";
import { useImmer } from "use-immer";
import { useTranslation } from "react-i18next";
import { useSnackbar } from "notistack";
import CircularProgress from "@material-ui/core/CircularProgress";
import { WelcomePanel } from "./Welcome";
import {
  QuestionPanel,
  ChallengeButton,
  QuestionAnswers,
  QuestionAnswer
} from "./Question";
import { Players, Player } from "./Players";
import { Center } from "./Layout";
import { openSocket } from "./Socket";
import { useMonitor } from "./AsyncHooks";

function Game() {
  const { t } = useTranslation();
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();
  const [socket, setSocket] = useState();
  const [username, setUsername] = useState();
  const [entering, handleEnter] = useMonitor(async username => {
    closeSnackbar();
    try {
      setSocket(await openSocket(username));
      setUsername(username);
    } catch (err) {
      enqueueSnackbar(t(err.message), {
        variant: "error"
      });
    }
  });
  if (!socket) {
    return (
      <Center>
        <WelcomePanel onEnter={handleEnter} entering={entering} />
      </Center>
    );
  }
  return <Session socket={socket} username={username} />;
}

function Session({ socket, username }) {
  const [session, updateSession] = useImmer({
    question: null,
    answers: [],
    answersStatus: [],
    answer: null,
    players: [],
    playersStatus: {},
    challenging: false
  });
  const handleChallenge = () => {
    updateSession(it => {
      it.challenging = true;
    });
    socket.sendJson({ action: "challenge" });
  };
  const handleAnswer = index => {
    updateSession(it => {
      it.answer = index;
      it.answers[index].status = "loading";
    });
    socket.sendJson({ answer: index });
  };
  socket.onmessage = message => {
    const data = JSON.parse(message.data);
    console.log("message:", data);
    switch (data.event) {
      case "question":
        return updateSession(it => {
          it.question = data.question;
          it.answers = [];
          it.answer = null;
          it.playersStatus = {};
          it.challenging = false;
        });
      case "joined":
        return updateSession(it => {
          it.players.push({ username: data.user });
        });
      case "challenged":
        // TODO: if I'm challenged start countdown
        return updateSession(it => {
          it.playersStatus[data.user] = "challenging";
          it.challenging = true;
        });
      case "reply":
        return updateSession(it => {
          it.answers = data.answers.map(text => ({ text }));
        });
      case "lost":
        return updateSession(it => {
          it.challenging = false;
          it.playersStatus[data.user] = "loser";
          if (data.user === username) {
            it.answers[it.answer].status = "failure";
          }
        });
      case "end":
        return updateSession(it => {
          it.playersStatus[data.winner] = "winner";
          if (data.winner === username) {
            it.answers[it.answer].status = "success";
          }
        });
      default:
        console.log("unexpected message", data);
    }
  };
  const {
    question,
    answers,
    answer,
    players,
    playersStatus,
    challenging
  } = session;
  return (
    <Fragment>
      <SessionPlayers players={players} status={playersStatus} />
      <Center>
        {question && (
          <SessionQuestion
            question={question}
            answers={answers}
            answer={answer}
            challenging={challenging}
            onChallenge={handleChallenge}
            onAnswer={handleAnswer}
          />
        )}
        {!question && <CircularProgress />}
      </Center>
    </Fragment>
  );
}

function SessionPlayers({ players, status }) {
  return (
    <Players>
      {players.map(player => (
        <Player
          key={player.username}
          username={player.username}
          status={status[player.username]}
        />
      ))}
    </Players>
  );
}

function SessionQuestion({
  question,
  answers,
  answer,
  challenging,
  onChallenge,
  onAnswer
}) {
  return (
    <QuestionPanel question={question}>
      {answers.length === 0 && (
        <ChallengeButton onChallenge={onChallenge} challenging={challenging} />
      )}
      {answers.length > 0 && (
        <QuestionAnswers>
          {answers.map(({ text, status }, index) => (
            <QuestionAnswer
              key={index}
              index={index}
              text={text}
              status={status}
              onSelect={answer !== null ? undefined : onAnswer}
            />
          ))}
        </QuestionAnswers>
      )}
    </QuestionPanel>
  );
}

export default Game;
