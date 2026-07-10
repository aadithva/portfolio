import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { animate } from "motion/mini";
import "./TrueFocus.css";

const normalizeWord = (word) =>
  word.toLowerCase().replace(/^[^a-z0-9]+|[^a-z0-9]+$/g, "");

const usePrefersReducedMotion = () => {
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
};

const TrueFocus = ({
  sentence = "True Focus",
  separator = " ",
  manualMode = false,
  blurAmount = 5,
  borderColor = "green",
  glowColor = "rgba(0, 255, 0, 0.6)",
  animationDuration = 0.5,
  pauseBetweenAnimations = 1,
  focusWords,
}) => {
  const words = useMemo(
    () => sentence.split(separator).filter(Boolean),
    [sentence, separator]
  );
  const focusWordsKey = Array.isArray(focusWords) ? focusWords.join("|") : "";
  const focusableIndices = useMemo(() => {
    if (!focusWordsKey) return words.map((_, index) => index);

    const selectedWords = new Set(
      focusWordsKey.split("|").map(normalizeWord).filter(Boolean)
    );
    return words.reduce((indices, word, index) => {
      if (selectedWords.has(normalizeWord(word))) indices.push(index);
      return indices;
    }, []);
  }, [focusWordsKey, words]);

  const reduceMotion = usePrefersReducedMotion();
  const [currentPosition, setCurrentPosition] = useState(0);
  const currentIndex = focusableIndices[currentPosition] ?? -1;
  const containerRef = useRef(null);
  const frameRef = useRef(null);
  const framePositionedRef = useRef(false);
  const wordRefs = useRef([]);
  const [frameReady, setFrameReady] = useState(false);
  const [focusRect, setFocusRect] = useState({
    x: 0,
    y: 0,
    width: 0,
    height: 0,
  });

  useEffect(() => {
    setCurrentPosition(0);
  }, [focusWordsKey, sentence, separator]);

  useEffect(() => {
    if (
      manualMode ||
      reduceMotion ||
      focusableIndices.length < 2
    ) {
      return undefined;
    }

    const intervalDuration =
      Math.max(0.05, animationDuration + pauseBetweenAnimations) * 1000;
    const interval = window.setInterval(() => {
      if (document.visibilityState !== "visible") return;
      setCurrentPosition(
        (previous) => (previous + 1) % focusableIndices.length
      );
    }, intervalDuration);

    return () => window.clearInterval(interval);
  }, [
    animationDuration,
    focusableIndices.length,
    manualMode,
    pauseBetweenAnimations,
    reduceMotion,
  ]);

  const syncFocusRect = useCallback(() => {
    const container = containerRef.current;
    const activeWord = wordRefs.current[currentIndex];

    if (!container || !activeWord) {
      setFrameReady(false);
      return;
    }

    const parentRect = container.getBoundingClientRect();
    const activeRect = activeWord.getBoundingClientRect();

    setFocusRect({
      x: activeRect.left - parentRect.left,
      y: activeRect.top - parentRect.top,
      width: activeRect.width,
      height: activeRect.height,
    });
    setFrameReady(true);
  }, [currentIndex]);

  useEffect(() => {
    let cancelled = false;
    const frame = window.requestAnimationFrame(syncFocusRect);
    const resizeObserver =
      "ResizeObserver" in window
        ? new ResizeObserver(syncFocusRect)
        : null;

    if (containerRef.current) resizeObserver?.observe(containerRef.current);
    if (wordRefs.current[currentIndex]) {
      resizeObserver?.observe(wordRefs.current[currentIndex]);
    }

    const handleResize = () => syncFocusRect();
    window.addEventListener("resize", handleResize);
    document.fonts?.ready.then(() => {
      if (!cancelled) syncFocusRect();
    });

    return () => {
      cancelled = true;
      window.cancelAnimationFrame(frame);
      resizeObserver?.disconnect();
      window.removeEventListener("resize", handleResize);
    };
  }, [currentIndex, syncFocusRect]);

  useEffect(() => {
    const frame = frameRef.current;
    if (!frame) return undefined;

    if (reduceMotion || !frameReady || currentIndex < 0) {
      frame.style.opacity = "0";
      framePositionedRef.current = false;
      return undefined;
    }

    const targetStyles = {
      transform: `translate3d(${focusRect.x}px, ${focusRect.y}px, 0)`,
      width: `${focusRect.width}px`,
      height: `${focusRect.height}px`,
      opacity: 1,
    };

    if (!framePositionedRef.current) {
      Object.assign(frame.style, targetStyles);
      framePositionedRef.current = true;
      return undefined;
    }

    const controls = animate(frame, targetStyles, {
      duration: animationDuration,
      ease: [0.2, 0, 0, 1],
    });
    return () => controls.stop();
  }, [
    animationDuration,
    currentIndex,
    focusRect,
    frameReady,
    reduceMotion,
  ]);

  const handleMouseEnter = (index) => {
    if (!manualMode) return;
    const nextPosition = focusableIndices.indexOf(index);
    if (nextPosition >= 0) setCurrentPosition(nextPosition);
  };

  return (
    <span className="true-focus" ref={containerRef}>
      <span className="true-focus__sr-only">{sentence}</span>

      {words.map((word, index) => {
        const isFocusable = focusableIndices.includes(index);
        const isActive = index === currentIndex;
        const shouldBlur =
          !reduceMotion && isFocusable && !isActive;

        return (
          <span
            key={`${word}-${index}`}
            ref={(element) => {
              wordRefs.current[index] = element;
            }}
            className={`true-focus__word ${
              manualMode && isFocusable ? "true-focus__word--manual" : ""
            }`}
            style={{
              filter: `blur(${shouldBlur ? blurAmount : 0}px)`,
              transition: reduceMotion
                ? "none"
                : `filter ${animationDuration}s var(--ds-ease-standard, ease)`,
            }}
            aria-hidden="true"
            onMouseEnter={() => handleMouseEnter(index)}
          >
            {word}
          </span>
        );
      })}

      <span
        className="true-focus__frame"
        aria-hidden="true"
        ref={frameRef}
        style={{
          "--border-color": borderColor,
          "--glow-color": glowColor,
          width: 0,
          height: 0,
          opacity: 0,
          transform: "translate3d(0, 0, 0)",
        }}
      >
        <span className="true-focus__corner true-focus__corner--top-left" />
        <span className="true-focus__corner true-focus__corner--top-right" />
        <span className="true-focus__corner true-focus__corner--bottom-left" />
        <span className="true-focus__corner true-focus__corner--bottom-right" />
      </span>
    </span>
  );
};

export default TrueFocus;
