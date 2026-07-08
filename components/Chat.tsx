"use client";

import { useEffect, useRef, useState } from "react";
import { api, AskResponse } from "@/lib/api";
import { ChatMessage, MessageCard } from "./MessageCard";

const STEPS = ["Understand", "Generate SQL", "Run query", "Visualize"];

export function Chat({ samples }: { samples: string[] }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(0);
  const counter = useRef(0);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const send = async (question: string) => {
    if (!question.trim() || busy) return;
    setInput("");
    const userMsg: ChatMessage = {
      id: ++counter.current,
      role: "user",
      content: question,
    };
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((prev) => [...prev, userMsg]);
    setBusy(true);
    setStep(0);

    // Animate pipeline steps while the request is in flight.
    const timers = [
      setTimeout(() => setStep(1), 400),
      setTimeout(() => setStep(2), 1200),
      setTimeout(() => setStep(3), 2000),
    ];

    try {
      const res: AskResponse = await api.ask(question, history);
      setMessages((prev) => [
        ...prev,
        { id: ++counter.current, role: "assistant", content: res.answer, data: res },
      ]);
    } catch (e) {
      const msg =
        e instanceof Error ? e.message : "Something went wrong contacting the API.";
      setMessages((prev) => [
        ...prev,
        {
          id: ++counter.current,
          role: "assistant",
          content: `⚠️ ${msg}. If this is a rate limit, wait a minute and retry.`,
        },
      ]);
    } finally {
      timers.forEach(clearTimeout);
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Suggested questions */}
      <div>
        <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Suggested questions
        </div>
        <div className="flex flex-wrap gap-2">
          {samples.map((q) => (
            <button key={q} onClick={() => send(q)} disabled={busy} className="pill-btn disabled:opacity-40">
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Conversation */}
      <div className="flex min-h-[240px] flex-col gap-4">
        {messages.length === 0 && (
          <div className="card p-8 text-center text-slate-400">
            Ask a question above, or type one below to get started.
          </div>
        )}
        {messages.map((m) => (
          <MessageCard key={m.id} msg={m} />
        ))}

        {busy && (
          <div className="flex gap-3">
            <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 text-sm text-white">
              ✦
            </div>
            <div className="card flex-1 p-4">
              <div className="flex flex-wrap gap-2">
                {STEPS.map((s, i) => (
                  <span
                    key={s}
                    className={`badge ${
                      i < step
                        ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                        : i === step
                        ? "border-indigo-300 bg-indigo-50 text-indigo-700"
                        : "border-slate-200 bg-slate-100 text-slate-400"
                    }`}
                  >
                    {i + 1}. {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="sticky bottom-4 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about revenue, orders, customers, or products…"
          className="flex-1 rounded-full border border-slate-200 bg-white px-5 py-3 text-slate-800 shadow-sm outline-none placeholder:text-slate-400 focus:border-indigo-400"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 px-6 py-3 font-semibold text-white shadow-sm transition hover:opacity-90 disabled:opacity-40"
        >
          Ask
        </button>
      </form>
    </div>
  );
}
