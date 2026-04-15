import { useState, useEffect } from "react"

import logoImage from "../assets/Vector.svg"
import ChatIcon from "../assets/chat.svg"
import PaperPlaneIcon from "../assets/paper-plane.svg"
import Robot from "../assets/Robot.mp4"
import ReactMarkdown from "react-markdown"
import { useRef } from "react"
import { Input, Button } from "@sg/uikit"
import remarkGfm from "remark-gfm"
import { formatDate } from "../utils/helper"

const BACKEND_URL = 'https://cyber.finrisk.sogaz.ru'
const COLLECTION_NAME = 'cyber_collection'
// const BACKEND_URL = "http://localhost:8080";

export function AdminPage() {
  const [isTyping, setIsTyping] = useState(false)
  const [inputValue, setInputValue] = useState("")

  const videoRef = useRef(null)

  // API Keys state
  const messagesEndRef = useRef(null)

  const [messages, setMessages] = useState(() => [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  // Стриминговый запрос к LLM
  const streamQuery = async (query) => {
    console.log(query)
    const history = messages.map(({ role, content }) => ({
      role,
      content,
    }))
    history.push({ role: "user", content: query })
    history.push({ role: "assistant", content: "" })

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: "user",
        content: query,
        timestamp: new Date(),
      },
      {
        id: Date.now() + 1,
        role: "assistant",
        content: "",
        timestamp: new Date(),
      },
    ])
    setIsTyping(true)

    try {
      const res = await fetch(`${BACKEND_URL}/chat/streaming/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          search_settings: {
            collection_name: "inspection_collection",
            email: "null",
            limit: 7,
            minimal_meta_score: 0.1,
          },
          dialog: {
            messages: history,
          },
        }),
      })

      if (!res.body) throw new Error("Нет потока ответа")

      const reader = res.body.getReader()
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const textChunk = new TextDecoder("utf-8").decode(value)
        buffer += textChunk

        setMessages((prev) => {
          // Обновить последний assistant message
          const updated = [...prev]
          for (let i = updated.length - 1; i >= 0; i--) {
            if (updated[i].role === "assistant") {
              updated[i] = {
                ...updated[i],
                content: buffer,
              }
              break
            }
          }
          return updated
        })
      }
    } catch (e) {
      console.log(e)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          role: "assistant",
          content: "Ошибка получения ответа от сервера.",
          timestamp: new Date(),
        },
      ])
    } finally {
      setIsTyping(false)
    }
  }

  const handleSend = async (event) => {
    event?.preventDefault()

    if (!inputValue.trim()) return
    await streamQuery(inputValue.trim())
    setInputValue("")
  }

  useEffect(() => {
    if (!videoRef.current) {
      return
    }

    videoRef.current.play().catch((error) => {
      console.error("Error with auto play video: ", error)
    })
  }, [])

  return (
    <div className="min-h-screen bg-[#f4f5f8] flex" data-oid="_8fa79l">
      {/* Sidebar */}
      <div
        className="bg-[#FFFFFF] flex flex-col border-r border-r-[#1A33731A]"
        data-oid="hxnx:86"
      >
        <div className="p-5" data-oid="7mbvmma">
          <div className="flex items-center justify-center" data-oid=":ge1i3e">
            <h2
              className="text-xl font-bold text-gray-800 flex gap-3"
              data-oid="kuxei-l"
            >
              <img src={logoImage} alt="" />
            </h2>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <form
        className="flex-1 flex flex-col"
        data-oid="h-q521x"
        onSubmit={handleSend}
      >
        {/* Header */}
        <header className="bg-white border-b h-[64px]" data-oid="-uicjnl">
          <div
            className="flex items-center justify-between py-[16px] px-[24px]"
            data-oid="3k:d00m"
          >
            <h1
              className="text-[20px] leading-[24px]] font-bold text-gray-800 flex justify-center"
              data-oid=".8i4a.2"
            >
              ИИ-ассистент
            </h1>
            <h1
              className="text-[16px] font-normal leading-[24px] text-[#152149]"
              data-oid=".8i4a.2"
            >
              Страхование киберрисков
            </h1>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 flex p-[24px]" data-oid="_wajmw7">
          <div
            className={`w-[100%] max-w-[872px] m-auto flex flex-col relative ${
              messages?.length === 0 ? "h-auto" : "h-[100%]"
            }`}
            data-oid="tjuq9bd"
          >
            {messages.length === 0 ? (
              <video
                ref={videoRef}
                className="mx-auto mb-[-47px]"
                controls={false}
                controlsList="nofullscreen"
                height={223}
                src={Robot}
                width={223}
                autoPlay
                loop
                muted
                playsInline
              />
            ) : null}

            <div
              className={`flex-1 flex flex-col border-0 rounded-[24px] bg-white ${
                messages?.length === 0 ? "min-h-[260px]" : ""
              }`}
            >
              <ul className="flex-1 overflow-y-auto p-[24px] space-y-6">
                {messages.length > 0 ? (
                  messages.map((message) => (
                    <li
                      key={message.id}
                      className={`flex ${
                        message.role === "assistant"
                          ? "justify-start mb-[24px]"
                          : "justify-end"
                      }`}
                      data-oid="ly1xb1x"
                    >
                      <div
                        className={`flex flex-wrap w-[100%] ${
                          message.role === "assistant"
                            ? "flex-row"
                            : "flex-row-reverse"
                        }`}
                        data-oid=".2:gipu"
                      >
                        <div
                          className={`${
                            message.role === "assistant"
                              ? "text-left w-[100%]"
                              : "text-right"
                          }`}
                          data-oid="c5om05_"
                        >
                          <div
                            className={`inline-block ${
                              message.role === "assistant"
                                ? " bg-white text-[#000078] text-[17x]"
                                : " bg-[#E8EDFC] text-[#000078] text-[17px] py-[8px] px-[16px] rounded-[16px] rounded-br-[4px]"
                            }`}
                            data-oid="m-1al7w"
                          >
                            <ReactMarkdown
                              // className="prose prose-invert max-w-none break-words leading-relaxed"
                              // unwrapDisallowed={true}
                              // disallowedElements={["p"]}
                              remarkPlugins={[remarkGfm]}
                              components={{
                                table: (props) => (
                                  <div className="overflow-x-auto my-4">
                                    <table
                                      {...props}
                                      className="
                                                                    w-full border-collapse 
                                                                    rounded-xl overflow-hidden 
                                                                    text-sm
                                                                    "
                                    />
                                  </div>
                                ),

                                thead: (props) => (
                                  <thead
                                    {...props}
                                    className="bg-gray-100 border-b border-gray-300 text-[#152149]"
                                  />
                                ),

                                tbody: (props) => (
                                  <tbody
                                    {...props}
                                    className="divide-y divide-gray-200"
                                  />
                                ),

                                tr: (props) => (
                                  <tr
                                    {...props}
                                    className="hover:bg-gray-50 transition-colors"
                                  />
                                ),
                                th: (props) => (
                                  <th
                                    {...props}
                                    className="
                                                                        px-4 py-3 
                                                                        font-semibold 
                                                                        text-left 
                                                                        border border-gray-300
                                                                        bg-gray-100
                                                                        text-[#152149]
                                                                        whitespace-normal
                                                                    "
                                  />
                                ),
                                td: (props) => (
                                  <td
                                    {...props}
                                    className="
                                                                            px-4 py-3 
                                                                            border border-gray-300 
                                                                            align-top 
                                                                            text-[#152149] 
                                                                            whitespace-normal
                                                                        "
                                  />
                                ),
                                p: (props) => (
                                  <p
                                    {...props}
                                    className="text-[14px] leading-[20px] text-[#152149]"
                                  />
                                ),
                                h1: (props) => (
                                  <h1
                                    {...props}
                                    className="text-2xl font-bold mt-4 mb-2 text-[#152149]"
                                  />
                                ),
                                h2: (props) => (
                                  <h2
                                    {...props}
                                    className="text-xl font-semibold mt-3 mb-2 text-[#152149]"
                                  />
                                ),
                                li: (props) => (
                                  <li
                                    {...props}
                                    className="ml-5 list-disc text-[#152149] text-[14px] "
                                  />
                                ),
                                code: (props) => (
                                  <code
                                    {...props}
                                    className="bg-slate-800 px-2 py-1 rounded text-sm font-mono text-green-300"
                                  />
                                ),
                                a: (props) => (
                                  <a
                                    {...props}
                                    className="text-blue-400 underline hover:text-blue-300 "
                                  />
                                ),
                              }}
                            >
                              {message.content}
                            </ReactMarkdown>
                          </div>
                          {message.role === "assistant" ? (
                            <p
                              className="text-[12px] text-[#15214999] mt-[16px]"
                              data-oid="-xfbwow"
                            >
                              {formatDate(message.timestamp)}
                            </p>
                          ) : null}
                        </div>

                        {message.role === "assistant" ? (
                          <div className="w-[100%] h-[1px] bg-[#1521491A] mt-[24px]" />
                        ) : null}
                      </div>
                    </li>
                  ))
                ) : (
                  // TODO: Сделать здесь заглушку при messages.length === 0
                  <li className="mt-[50px]">
                    <h3 className="text-[#152149] text-[36px] text-center font-light">
                      Чем могу вам помочь?
                    </h3>
                  </li>
                )}

                {isTyping && (
                  <div className="flex justify-start" data-oid="ybmttm4">
                    <div className="flex max-w-3xl" data-oid="3kisgvd">
                      <div className="mx-3" data-oid="yux77_i">
                        <div
                          className="inline-block p-4 rounded-2xl bg-slate-700/50"
                          data-oid="uka3erd"
                        >
                          <div className="flex space-x-1" data-oid="i0m0976">
                            <div
                              className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                              data-oid="u4hj_ik"
                            />
                            <div
                              className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                              style={{ animationDelay: "0.1s" }}
                              data-oid="2.2z2jb"
                            />
                            <div
                              className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                              style={{ animationDelay: "0.2s" }}
                              data-oid="h0hk:rx"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} data-oid="9tn2ic6" />
              </ul>

              {/* Input Area */}
              <div
                className="border-slate-700/50 rounded-[24px] bg-white p-[8px] shadow-[2px_0px_11px_0px_#1521490D] shadow-[1px_0px_1px_0px_#1521490A] mt-auto"
                data-oid="oqjk_r4"
              >
                <div
                  className="flex space-x-4 text-[#000078]"
                  data-oid="n888g0a"
                >
                  <div className="flex-1 mr-[8px]" data-oid="ttjvfzq">
                    <Input
                      id="input"
                      label="Введите ваш вопрос"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onClear={() => setInputValue("")}
                      placeholder="Введите ваш вопрос"
                      size="xl"
                    />
                  </div>
                  <Button
                    onlyIcon
                    startIcon={
                      <img src={PaperPlaneIcon} alt="Бумажный самолет" />
                    }
                    disabled={!inputValue.trim() || isTyping}
                    size={52}
                    onClick={handleSend}
                    type="submit"
                    variant="primary"
                  />
                </div>
              </div>
            </div>
          </div>
        </main>
      </form>

      <style data-oid=":9_0_3h">{`
                :root {
                    font-family: system-ui, Avenir, Helvetica, Arial, sans-serif;
                    line-height: 1.5;
                    font-weight: 400;
                }
                .slider::-webkit-slider-thumb {
                    appearance: none;
                    height: 15px;
                    width: 15px;
                    border-radius: 50%;
                    background: linear-gradient(45deg, #ffffffff, #ffffffff);
                    cursor: pointer;
                    border: 0.2px solid #7c7e81ff;
                    box-shadow: 5px 3px 3px -3px rgba(34, 60, 80, 0.2);
                }
            `}</style>
    </div>
  )
}
