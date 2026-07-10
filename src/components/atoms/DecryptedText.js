import {
  createElement,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { span as MotionSpan } from "motion/react-m";
import "./DecryptedText.css";

const styles = {
  wrapper: {
    display: "inline-block",
    whiteSpace: "pre-wrap",
  },
  srOnly: {
    position: "absolute",
    width: "1px",
    height: "1px",
    padding: 0,
    margin: "-1px",
    overflow: "hidden",
    clip: "rect(0,0,0,0)",
    whiteSpace: "nowrap",
    border: 0,
  },
};

function usePrefersReducedMotion() {
  const [reduceMotion, setReduceMotion] = useState(() =>
    typeof window === "undefined"
      ? false
      : window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const syncPreference = () => setReduceMotion(preference.matches);
    preference.addEventListener("change", syncPreference);
    return () => preference.removeEventListener("change", syncPreference);
  }, []);

  return reduceMotion;
}

export default function DecryptedText({
  text = "",
  speed = 50,
  maxIterations = 10,
  sequential = false,
  revealDirection = "start",
  useOriginalCharsOnly = false,
  characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+",
  className = "",
  parentClassName = "",
  encryptedClassName = "",
  animateOn = "hover",
  clickMode = "once",
  ...props
}) {
  const reduceMotion = usePrefersReducedMotion();
  const [displayText, setDisplayText] = useState(text);
  const [isAnimating, setIsAnimating] = useState(false);
  const [revealedIndices, setRevealedIndices] = useState(new Set());
  const [hasAnimated, setHasAnimated] = useState(false);
  const [isDecrypted, setIsDecrypted] = useState(animateOn !== "click");
  const [direction, setDirection] = useState("forward");

  const containerRef = useRef(null);
  const orderRef = useRef([]);
  const pointerRef = useRef(0);
  const intervalRef = useRef(null);

  const availableChars = useMemo(() => {
    const pool = useOriginalCharsOnly
      ? Array.from(new Set(text.split(""))).filter((char) => !/\s/.test(char))
      : characters.split("");
    return pool.length > 0 ? pool : ["·"];
  }, [useOriginalCharsOnly, text, characters]);

  const shuffleText = useCallback(
    (originalText, currentRevealed) =>
      originalText
        .split("")
        .map((char, index) => {
          if (/\s/.test(char)) return char;
          if (currentRevealed.has(index)) return originalText[index];
          return availableChars[
            Math.floor(Math.random() * availableChars.length)
          ];
        })
        .join(""),
    [availableChars]
  );

  const computeOrder = useCallback(
    (length) => {
      const order = [];
      if (length <= 0) return order;

      if (revealDirection === "start") {
        for (let index = 0; index < length; index += 1) order.push(index);
        return order;
      }

      if (revealDirection === "end") {
        for (let index = length - 1; index >= 0; index -= 1) order.push(index);
        return order;
      }

      const middle = Math.floor(length / 2);
      let offset = 0;
      while (order.length < length) {
        if (offset % 2 === 0) {
          const index = middle + offset / 2;
          if (index >= 0 && index < length) order.push(index);
        } else {
          const index = middle - Math.ceil(offset / 2);
          if (index >= 0 && index < length) order.push(index);
        }
        offset += 1;
      }
      return order.slice(0, length);
    },
    [revealDirection]
  );

  const fillAllIndices = useCallback(
    () => new Set(Array.from({ length: text.length }, (_, index) => index)),
    [text]
  );

  const removeRandomIndices = useCallback((set, count) => {
    const indices = Array.from(set);
    for (let index = 0; index < count && indices.length > 0; index += 1) {
      indices.splice(Math.floor(Math.random() * indices.length), 1);
    }
    return new Set(indices);
  }, []);

  const encryptInstantly = useCallback(() => {
    const emptySet = new Set();
    setRevealedIndices(emptySet);
    setDisplayText(shuffleText(text, emptySet));
    setIsDecrypted(false);
  }, [text, shuffleText]);

  const triggerDecrypt = useCallback(() => {
    if (reduceMotion) {
      setDisplayText(text);
      setIsDecrypted(true);
      setIsAnimating(false);
      return;
    }

    if (sequential) {
      orderRef.current = computeOrder(text.length);
      pointerRef.current = 0;
    }

    const emptySet = new Set();
    setRevealedIndices(emptySet);
    setDisplayText(shuffleText(text, emptySet));
    setDirection("forward");
    setIsAnimating(true);
  }, [computeOrder, reduceMotion, sequential, shuffleText, text]);

  const triggerReverse = useCallback(() => {
    if (reduceMotion) return;

    const fullSet = fillAllIndices();
    if (sequential) {
      orderRef.current = computeOrder(text.length).slice().reverse();
      pointerRef.current = 0;
    }
    setRevealedIndices(fullSet);
    setDisplayText(shuffleText(text, fullSet));
    setDirection("reverse");
    setIsAnimating(true);
  }, [
    computeOrder,
    fillAllIndices,
    reduceMotion,
    sequential,
    shuffleText,
    text,
  ]);

  useEffect(() => {
    if (!isAnimating || reduceMotion) return undefined;

    let currentIteration = 0;

    const getNextIndex = (revealedSet) => {
      const textLength = text.length;
      if (revealDirection === "start") return revealedSet.size;
      if (revealDirection === "end") {
        return textLength - 1 - revealedSet.size;
      }

      const middle = Math.floor(textLength / 2);
      const offset = Math.floor(revealedSet.size / 2);
      const candidate =
        revealedSet.size % 2 === 0
          ? middle + offset
          : middle - offset - 1;

      if (
        candidate >= 0 &&
        candidate < textLength &&
        !revealedSet.has(candidate)
      ) {
        return candidate;
      }

      for (let index = 0; index < textLength; index += 1) {
        if (!revealedSet.has(index)) return index;
      }
      return 0;
    };

    intervalRef.current = window.setInterval(() => {
      setRevealedIndices((previous) => {
        if (sequential && direction === "forward") {
          if (previous.size < text.length) {
            const next = new Set(previous);
            next.add(getNextIndex(previous));
            setDisplayText(shuffleText(text, next));
            return next;
          }
          window.clearInterval(intervalRef.current);
          setIsAnimating(false);
          setIsDecrypted(true);
          return previous;
        }

        if (sequential && direction === "reverse") {
          if (pointerRef.current < orderRef.current.length) {
            const next = new Set(previous);
            next.delete(orderRef.current[pointerRef.current]);
            pointerRef.current += 1;
            setDisplayText(shuffleText(text, next));
            if (next.size === 0) {
              window.clearInterval(intervalRef.current);
              setIsAnimating(false);
              setIsDecrypted(false);
            }
            return next;
          }
          window.clearInterval(intervalRef.current);
          setIsAnimating(false);
          setIsDecrypted(false);
          return previous;
        }

        if (direction === "forward") {
          setDisplayText(shuffleText(text, previous));
          currentIteration += 1;
          if (currentIteration >= maxIterations) {
            window.clearInterval(intervalRef.current);
            setIsAnimating(false);
            setDisplayText(text);
            setIsDecrypted(true);
          }
          return previous;
        }

        const currentSet =
          previous.size === 0 ? fillAllIndices() : previous;
        const removeCount = Math.max(
          1,
          Math.ceil(text.length / Math.max(1, maxIterations))
        );
        const next = removeRandomIndices(currentSet, removeCount);
        setDisplayText(shuffleText(text, next));
        currentIteration += 1;

        if (next.size === 0 || currentIteration >= maxIterations) {
          window.clearInterval(intervalRef.current);
          setIsAnimating(false);
          setIsDecrypted(false);
          setDisplayText(shuffleText(text, new Set()));
          return new Set();
        }
        return next;
      });
    }, speed);

    return () => window.clearInterval(intervalRef.current);
  }, [
    direction,
    fillAllIndices,
    isAnimating,
    maxIterations,
    reduceMotion,
    removeRandomIndices,
    revealDirection,
    sequential,
    shuffleText,
    speed,
    text,
  ]);

  const handleClick = () => {
    if (animateOn !== "click") return;
    if (clickMode === "once") {
      if (!isDecrypted) triggerDecrypt();
      return;
    }
    if (isDecrypted) triggerReverse();
    else triggerDecrypt();
  };

  const triggerHoverDecrypt = useCallback(() => {
    if (isAnimating || reduceMotion) return;
    setRevealedIndices(new Set());
    setIsDecrypted(false);
    setDisplayText(text);
    setDirection("forward");
    setIsAnimating(true);
  }, [isAnimating, reduceMotion, text]);

  const resetToPlainText = useCallback(() => {
    window.clearInterval(intervalRef.current);
    setIsAnimating(false);
    setRevealedIndices(new Set());
    setDisplayText(text);
    setIsDecrypted(true);
    setDirection("forward");
  }, [text]);

  useEffect(() => {
    if (
      reduceMotion ||
      (animateOn !== "view" && animateOn !== "inViewHover")
    ) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated) {
            triggerDecrypt();
            setHasAnimated(true);
          }
        });
      },
      { root: null, rootMargin: "0px", threshold: 0.1 }
    );

    const current = containerRef.current;
    if (current) observer.observe(current);
    return () => {
      if (current) observer.unobserve(current);
    };
  }, [animateOn, hasAnimated, reduceMotion, triggerDecrypt]);

  useEffect(() => {
    if (reduceMotion) {
      resetToPlainText();
    } else if (animateOn === "click") {
      encryptInstantly();
    } else {
      setDisplayText(text);
      setIsDecrypted(true);
    }
    setRevealedIndices(new Set());
    setDirection("forward");
  }, [animateOn, encryptInstantly, reduceMotion, resetToPlainText, text]);

  const animateProps =
    animateOn === "hover" || animateOn === "inViewHover"
      ? {
          onMouseEnter: triggerHoverDecrypt,
          onMouseLeave: resetToPlainText,
        }
      : animateOn === "click"
        ? { onClick: handleClick }
        : {};

  return createElement(
    MotionSpan,
    {
      className: parentClassName,
      ref: containerRef,
      style: styles.wrapper,
      ...animateProps,
      ...props,
    },
    createElement("span", { style: styles.srOnly }, text),
    createElement(
      "span",
      { "aria-hidden": "true" },
      displayText.split("").map((char, index) => {
        const revealed =
          revealedIndices.has(index) || (!isAnimating && isDecrypted);
        return createElement(
          "span",
          {
            key: index,
            className: revealed ? className : encryptedClassName,
          },
          char
        );
      })
    )
  );
}
