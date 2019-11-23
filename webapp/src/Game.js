import _ from "lodash";
import React, { useEffect, useState, Fragment } from "react";
import { useImmer } from "use-immer";
import { useTranslation } from "react-i18next";
import { useSnackbar } from "notistack";
import CircularProgress from "@material-ui/core/CircularProgress";
import { Welcome } from "./Welcome";
import {
  QuestionPanel,
  ChallengeButton,
  QuestionAnswers,
  QuestionAnswer
} from "./Question";
import { Players, Player } from "./Players";
import { Countdown, useCountdown } from "./Countdown";
import { Center } from "./Layout";
import { openSocket } from "./Socket";
import { createBrowserHistory } from "history";

const history = createBrowserHistory();

function Game() {
  const { t } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();
  const [connection, setConnection] = useState(null);
  const handleLogin = connection => {
    setConnection(connection);
    saveUsername(connection.username);
  };
  const handleError = err => {
    enqueueSnackbar(t(err.message || "Something goes wrong..."), {
      variant: "warning"
    });
  };
  const handleExit = () => setConnection(null);
  const saveUsername = username => {
    history.push(`?uid=${username}`);
  };
  const getUsername = () => {
    return new URLSearchParams(history.location.search).get("uid");
  };
  if (!connection) {
    return (
      <Login
        initialUsername={getUsername()}
        onLogin={handleLogin}
        onError={handleError}
      />
    );
  }
  return <Session {...connection} onExit={handleExit} />;
}

function Login({ initialUsername, onLogin, onError }) {
  const [autoLogin, setAutoLogin] = useState(Boolean(initialUsername));
  const [entering, setEntering] = useState(false);
  const handleEnter = async username => {
    try {
      setEntering(true);
      const socket = await openSocket(username);
      onLogin({ socket, username });
    } catch (err) {
      setEntering(false);
      setAutoLogin(false);
      onError(err);
    }
  };
  useEffect(() => {
    if (autoLogin) handleEnter(initialUsername);
  }, []);
  return (
    <Center>
      {autoLogin && <CircularProgress />}
      {!autoLogin && <Welcome onEnter={handleEnter} entering={entering} />}
    </Center>
  );
}

function Session({ socket, username, onExit }) {
  const { t } = useTranslation();
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();
  const [session, updateSession] = useImmer({
    players: []
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
        closeSnackbar();
        return updateSession(it => {
          it.question = data.question;
          it.answers = [];
          it.answer = null;
          it.playersStatus = {};
          it.challenging = false;
          it.acceptAnswer = true;
        });
      case "joined":
        return updateSession(it => {
          it.players.push({ username: data.user });
        });
      case "left":
        enqueueSnackbar(t("{{user}} has left the game", data));
        return updateSession(it => {
          const index = _.findIndex(it.players, it => it.username === data.user);
          if (index >= 0) it.players.splice(index, 1);
        });
      case "challenged":
        return updateSession(it => {
          it.playersStatus[data.user] = "challenging";
          it.challenging = true;
        });
      case "reply":
        return updateSession(it => {
          it.answers = data.answers.map(text => ({ text }));
          it.replyTimeout = data.timeout;
        });
      case "lost":
        if (data.reason) {
          enqueueSnackbar(t(`{{user}} is out due to ${data.reason}`, data), {
            variant: "error"
          });
        }
        return updateSession(it => {
          it.challenging = false;
          it.playersStatus[data.user] = "loser";
          if (data.user === username) {
            if (it.answer !== null) {
              it.answers[it.answer].status = "failure";
            }
            it.acceptAnswer = false;
          }
        });
      case "end":
        if (data.winner) {
          enqueueSnackbar(t(`{{winner}} won!`, data), {
            variant: "success"
          });
        } else {
          enqueueSnackbar(t(`Nobody won!`, data), {
            variant: "warning"
          });
        }
        return updateSession(it => {
          if (data.winner) {
            it.playersStatus[data.winner] = "winner";
          }
          if (it.answers.length > 0) {
            it.answers[data.answer].status = "success";
          }
        });
      default:
        console.log("unexpected message", data);
    }
  };
  socket.onclose = onExit;
  const {
    question,
    answers,
    answer,
    acceptAnswer,
    replyTimeout,
    players,
    playersStatus,
    challenging
  } = session;
  return (
    <Fragment>
      <SessionPlayers players={players} status={playersStatus} />
      <Center responsive={true}>
        {question && (
          <SessionQuestion
            active={acceptAnswer}
            question={question}
            answers={answers}
            answer={answer}
            challenging={challenging}
            timeoutSeconds={replyTimeout}
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
  active,
  question,
  answers,
  answer,
  challenging,
  timeoutSeconds,
  onChallenge,
  onAnswer
}) {
  const answering = answers.length > 0 && active && answer === null
  return (
    <Fragment>
      <QuestionPanel question={question}>
        {answers.length === 0 && (
          <ChallengeButton
            onChallenge={onChallenge}
            challenging={challenging}
            enabled={active}
          />
        )}
        {answers.length > 0 && (
          <QuestionAnswers>
            {answers.map(({ text, status }, index) => (
              <QuestionAnswer
                key={index}
                index={index}
                text={text}
                status={status}
                onSelect={answering ? onAnswer : undefined}
              />
            ))}
          </QuestionAnswers>
        )}
      </QuestionPanel>
      {answering && <SessionCountdown seconds={timeoutSeconds} />}
    </Fragment>
  );
}

function SessionCountdown({ seconds }) {
  const [total, current] = useCountdown(seconds);
  return <Countdown total={total} current={current} />;
}

export default Game;
