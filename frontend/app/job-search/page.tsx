"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Upload from "lucide-react/dist/esm/icons/upload.js"
import Search from "lucide-react/dist/esm/icons/search.js"
import Zap from "lucide-react/dist/esm/icons/zap.js"
import MapPin from "lucide-react/dist/esm/icons/map-pin.js"
import Clock from "lucide-react/dist/esm/icons/clock.js"
import DollarSign from "lucide-react/dist/esm/icons/dollar-sign.js"
import Target from "lucide-react/dist/esm/icons/target.js"
import Download from "lucide-react/dist/esm/icons/download.js"
import AlertTriangle from "lucide-react/dist/esm/icons/alert-triangle.js"
import Heart from "lucide-react/dist/esm/icons/heart.js"
import { cn } from "@/lib/utils"

interface Job {
  id: string
  title: string
  company: string
  location: string
  salary: string
  description: string
  matchScore: number
  postedDate: string
  type: string
  difficulty: "legendary" | "elite" | "veteran" | "rookie"
}

type ProcessingStep = "scanning" | "infiltrating" | "calculating"

export default function JobSearchTool() {
  const [resume, setResume] = useState<File | null>(null)
  const [jobUrl, setJobUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState<ProcessingStep>("scanning")
  const [jobs, setJobs] = useState<Job[]>([])
  const [searchComplete, setSearchComplete] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [progress, setProgress] = useState(0)
  const [glitchText, setGlitchText] = useState("GET A JOB")
  const [radarAngle, setRadarAngle] = useState(0)
  const [radarBlips, setRadarBlips] = useState<
    Array<{ id: number; x: number; y: number; size: number; opacity: number; color: string }>
  >([])
  const [anomalyBlips, setAnomalyBlips] = useState<
    Array<{ id: number; x: number; y: number; size: number; opacity: number; color: string }>
  >([])
  const radarRef = useRef<HTMLDivElement>(null)

  // Removed mockJobs. All job data must come from the backend API.

  useEffect(() => {
    // Radar animation
    const radarInterval = setInterval(() => {
      setRadarAngle((prev) => (prev + 2) % 360)
    }, 50)

    // Generate normal radar blips (when not loading)
    const generateBlips = () => {
      if (!isLoading) {
        const newBlips: Array<{ id: number; x: number; y: number; size: number; opacity: number; color: string }> = []
        const count = Math.floor(Math.random() * 2) + 1 // 1-2 new blips

        for (let i = 0; i < count; i++) {
          const angle = Math.random() * Math.PI * 2
          const distance = Math.random() * 0.8
          const x = 50 + Math.cos(angle) * distance * 50
          const y = 50 + Math.sin(angle) * distance * 50

          newBlips.push({
            id: Date.now() + i,
            x,
            y,
            size: Math.random() * 2 + 1,
            opacity: 0.8,
            color: "green",
          })
        }

        setRadarBlips((prev) =>
          [
            ...prev
              .filter((blip) => blip.opacity > 0.1)
              .map((blip) => ({
                ...blip,
                opacity: blip.opacity * 0.95,
              })),
            ...newBlips,
          ].slice(0, 15),
        )
      }
    }

    // Generate anomaly blips during loading
    const generateAnomalies = () => {
      if (isLoading) {
        const newAnomalies: Array<{ id: number; x: number; y: number; size: number; opacity: number; color: string }> = []
        const count = Math.floor(Math.random() * 5) + 3 // 3-7 anomalies

        for (let i = 0; i < count; i++) {
          const angle = Math.random() * Math.PI * 2
          const distance = Math.random() * 0.9
          const x = 50 + Math.cos(angle) * distance * 50
          const y = 50 + Math.sin(angle) * distance * 50

          // Different colors for different threat levels
          const colors = ["red", "orange", "yellow", "lime"]
          const color = colors[Math.floor(Math.random() * colors.length)]

          newAnomalies.push({
            id: Date.now() + i,
            x,
            y,
            size: Math.random() * 4 + 2, // Larger for anomalies
            opacity: 0.9,
            color,
          })
        }

        setAnomalyBlips((prev) =>
          [
            ...prev
              .filter((blip) => blip.opacity > 0.1)
              .map((blip) => ({
                ...blip,
                opacity: blip.opacity * 0.92,
              })),
            ...newAnomalies,
          ].slice(0, 25),
        )
      } else {
        // Clear anomalies when not loading
        setAnomalyBlips([])
      }
    }

    const blipInterval = setInterval(generateBlips, 2000)
    const anomalyInterval = setInterval(generateAnomalies, 800)

    // Glitch effect for title
    const glitchInterval = setInterval(() => {
      const glitchChars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
      const original = "GET A JOB"
      let glitched = ""

      for (let i = 0; i < original.length; i++) {
        if (Math.random() < 0.1) {
          glitched += glitchChars[Math.floor(Math.random() * glitchChars.length)]
        } else {
          glitched += original[i]
        }
      }

      setGlitchText(glitched)

      setTimeout(() => setGlitchText("GET A JOB"), 100)
    }, 3000)

    return () => {
      clearInterval(radarInterval)
      clearInterval(blipInterval)
      clearInterval(anomalyInterval)
      clearInterval(glitchInterval)
    }
  }, [isLoading])

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setResume(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResume(e.target.files[0])
    }
  }

  const handleSearch = async () => {
    if (!resume || !jobUrl) return

    setIsLoading(true)
    setSearchComplete(false)
    setProgress(0)

    // Scanning phase
    setCurrentStep("scanning")
    for (let i = 0; i <= 33; i++) {
      setProgress(i)
      await new Promise((resolve) => setTimeout(resolve, 40))
    }

    // Infiltrating phase
    setCurrentStep("infiltrating")
    for (let i = 34; i <= 66; i++) {
      setProgress(i)
      await new Promise((resolve) => setTimeout(resolve, 35))
    }

    // Calculating phase
    setCurrentStep("calculating")
    for (let i = 67; i <= 100; i++) {
      setProgress(i)
      await new Promise((resolve) => setTimeout(resolve, 30))
    }

    // setJobs(mockJobs) // Removed: do not set fallback jobs. Only set jobs from backend response.
    setIsLoading(false)
    setSearchComplete(true)
  }

  const resetSearch = () => {
    setResume(null)
    setJobUrl("")
    setIsLoading(false)
    setSearchComplete(false)
    setJobs([])
    setProgress(0)
  }

  const getMatchColor = (score: number) => {
    if (score >= 90) return "from-lime-400 to-green-400"
    if (score >= 80) return "from-orange-400 to-red-400"
    if (score >= 70) return "from-yellow-400 to-orange-400"
    return "from-red-400 to-red-600"
  }

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case "legendary":
        return "text-purple-400 bg-purple-900/30 border-purple-400"
      case "elite":
        return "text-red-400 bg-red-900/30 border-red-400"
      case "veteran":
        return "text-orange-400 bg-orange-900/30 border-orange-400"
      case "rookie":
        return "text-lime-400 bg-lime-900/30 border-lime-400"
      default:
        return "text-gray-400 bg-gray-900/30 border-gray-400"
    }
  }

  const getStepIcon = (step: ProcessingStep) => {
    switch (step) {
      case "scanning":
        return <Search className="h-6 w-6" />
      case "infiltrating":
        return <Target className="h-6 w-6" />
      case "calculating":
        return <Search className="h-6 w-6" />
    }
  }

  const renderHearts = (score: number) => {
    const getHeartFill = (heartIndex: number, score: number) => {
      // Each heart represents 20% (100% ÷ 5 hearts)
      // Heart 1: 0-20%, Heart 2: 20-40%, Heart 3: 40-60%, Heart 4: 60-80%, Heart 5: 80-100%
      const heartStartValue = heartIndex * 20
      const heartEndValue = (heartIndex + 1) * 20

      if (score >= heartEndValue) {
        return "full" // Score is above this heart's range
      } else if (score > heartStartValue) {
        // Score falls within this heart's range - calculate partial fill
        const progressInHeart = score - heartStartValue
        const percentageInHeart = (progressInHeart / 20) * 100

        if (percentageInHeart >= 87.5) return "full" // 17.5/20 = 87.5%
        if (percentageInHeart >= 62.5) return "three-quarter" // 12.5/20 = 62.5%
        if (percentageInHeart >= 37.5) return "half" // 7.5/20 = 37.5%
        if (percentageInHeart >= 12.5) return "quarter" // 2.5/20 = 12.5%
        return "empty"
      } else {
        return "empty" // Score is below this heart's range
      }
    }

    return (
      <div className="flex items-center gap-1">
        {Array.from({ length: 5 }, (_, i) => {
          const fillType = getHeartFill(i, score)
          return (
            <div key={i} className="relative">
              <Heart className="h-5 w-5 text-gray-600 fill-transparent" />
              {fillType !== "empty" && (
                <div
                  className="absolute inset-0 overflow-hidden"
                  style={{
                    clipPath:
                      fillType === "full"
                        ? "none"
                        : fillType === "three-quarter"
                          ? "polygon(0 0, 75% 0, 75% 100%, 0 100%)"
                          : fillType === "half"
                            ? "polygon(0 0, 50% 0, 50% 100%, 0 100%)"
                            : "polygon(0 0, 25% 0, 25% 100%, 0 100%)",
                  }}
                >
                  <Heart className="h-5 w-5 text-red-400 fill-red-400" />
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  const getBlipColor = (color: string) => {
    switch (color) {
      case "red":
        return "bg-red-400"
      case "orange":
        return "bg-orange-400"
      case "yellow":
        return "bg-yellow-400"
      case "lime":
        return "bg-lime-400"
      case "green":
      default:
        return "bg-green-400"
    }
  }

  const getBlipShadow = (color: string) => {
    switch (color) {
      case "red":
        return "0 0 8px rgba(248, 113, 113, 0.8)"
      case "orange":
        return "0 0 8px rgba(251, 146, 60, 0.8)"
      case "yellow":
        return "0 0 8px rgba(250, 204, 21, 0.8)"
      case "lime":
        return "0 0 8px rgba(163, 230, 53, 0.8)"
      case "green":
      default:
        return "0 0 8px rgba(74, 222, 128, 0.8)"
    }
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Military Radar - Background when not loading */}
      {!isLoading && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div ref={radarRef} className="w-[800px] h-[800px] relative opacity-20">
            {/* Radar circles */}
            <div className="absolute inset-0 border-2 border-green-500 rounded-full"></div>
            <div className="absolute inset-[15%] border border-green-500 rounded-full"></div>
            <div className="absolute inset-[30%] border border-green-500 rounded-full"></div>
            <div className="absolute inset-[45%] border border-green-500 rounded-full"></div>
            <div className="absolute inset-[60%] border border-green-500 rounded-full"></div>
            <div className="absolute inset-[75%] border border-green-500 rounded-full"></div>

            {/* Radar cross lines */}
            <div className="absolute top-1/2 left-0 right-0 h-px bg-green-500/50"></div>
            <div className="absolute top-0 bottom-0 left-1/2 w-px bg-green-500/50"></div>

            {/* Radar sweep */}
            <div
              className="absolute top-1/2 left-1/2 w-[50%] h-1 bg-gradient-to-r from-green-500 to-transparent origin-left"
              style={{
                transform: `translateX(-1px) translateY(-0.5px) rotate(${radarAngle}deg)`,
                boxShadow: "0 0 10px rgba(0, 255, 0, 0.7)",
              }}
            ></div>

            {/* Normal radar blips */}
            {radarBlips.map((blip) => (
              <div
                key={blip.id}
                className={cn("absolute rounded-full animate-ping-slow", getBlipColor(blip.color))}
                style={{
                  left: `${blip.x}%`,
                  top: `${blip.y}%`,
                  width: `${blip.size}px`,
                  height: `${blip.size}px`,
                  opacity: blip.opacity,
                  boxShadow: getBlipShadow(blip.color),
                }}
              ></div>
            ))}

            {/* Radar coordinates */}
            <div className="absolute top-1 left-1 text-green-500 text-xs font-mono">N 40°45'12.3"</div>
            <div className="absolute bottom-1 right-1 text-green-500 text-xs font-mono">E 73°58'44.1"</div>
            <div className="absolute top-1 right-1 text-green-500 text-xs font-mono">RANGE: 50KM</div>
            <div className="absolute bottom-1 left-1 text-green-500 text-xs font-mono">
              TARGETS: {radarBlips.length}
            </div>
          </div>
        </div>
      )}

      {/* Grid Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `
            linear-gradient(rgba(255,165,0,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,165,0,0.1) 1px, transparent 1px)
          `,
            backgroundSize: "50px 50px",
          }}
        />
      </div>

      {/* Rust/Damage Overlays */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-radial from-orange-900/20 to-transparent rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-radial from-red-900/20 to-transparent rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-orange-600/5 to-transparent rounded-full blur-3xl" />

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-16 animate-fade-in-up">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative">
              <AlertTriangle className="h-12 w-12 text-orange-400 animate-pulse" />
              <div className="absolute inset-0 h-12 w-12 text-orange-400 animate-ping opacity-30">
                <AlertTriangle className="h-12 w-12" />
              </div>
            </div>
            <h1 className="text-7xl font-black bg-gradient-to-r from-orange-400 via-red-400 to-orange-600 bg-clip-text text-transparent font-mono tracking-wider glitch-text">
              {glitchText}
            </h1>
          </div>
          <div className="space-y-4">
            <p className="text-2xl font-bold text-orange-400 font-mono tracking-wide">TAKE THE LEAP</p>
            <p className="text-lg text-gray-300 max-w-4xl mx-auto leading-relaxed">
              The wasteland is harsh, but opportunity awaits those brave enough to jump. Upload your combat record and
              infiltrate the job networks.
              <span className="text-orange-400 font-semibold"> Fortune favors the bold.</span>
            </p>
          </div>
        </div>

        {!isLoading && !searchComplete && (
          <div className="max-w-2xl mx-auto animate-fade-in-up animation-delay-300">
            <Card className="bg-gray-900/80 backdrop-blur-xl border-orange-600/30 shadow-2xl shadow-orange-500/10 border-2">
              <CardHeader className="text-center border-b border-orange-600/20">
                <CardTitle className="text-2xl font-bold text-white flex items-center justify-center gap-3 font-mono">
                  <Zap className="h-6 w-6 text-orange-400 animate-pulse" />
                  INITIATE PROTOCOL
                  <Zap className="h-6 w-6 text-orange-400 animate-pulse" />
                </CardTitle>
                <CardDescription className="text-gray-400 text-lg font-mono">
                  Two steps to breach the system
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-8 p-8">
                {/* Resume Upload */}
                <div className="space-y-4">
                  <label className="text-sm font-bold text-orange-400 uppercase tracking-widest font-mono flex items-center gap-2">
                    <span className="w-6 h-6 bg-orange-400 text-black rounded flex items-center justify-center text-xs font-black">
                      1
                    </span>
                    UPLOAD COMBAT RECORD
                  </label>
                  <div
                    className={cn(
                      "border-2 border-dashed rounded-lg p-12 text-center transition-all duration-500 cursor-pointer group relative overflow-hidden",
                      dragActive
                        ? "border-orange-400 bg-orange-400/10 shadow-lg shadow-orange-400/20"
                        : resume
                          ? "border-lime-400 bg-lime-400/10 shadow-lg shadow-lime-400/20"
                          : "border-gray-600 hover:border-orange-400 hover:bg-orange-400/5 hover:shadow-lg hover:shadow-orange-400/10",
                    )}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById("resume-upload")?.click()}
                  >
                    <input
                      id="resume-upload"
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    <div className="relative z-10">
                      <Upload
                        className={cn(
                          "h-16 w-16 mx-auto mb-4 transition-all duration-500 group-hover:scale-110",
                          resume ? "text-lime-400" : "text-gray-400 group-hover:text-orange-400",
                        )}
                      />
                      {resume && (
                        <div className="absolute -top-2 -right-2 w-8 h-8 bg-lime-400 rounded-full flex items-center justify-center animate-pulse">
                          <span className="text-black text-sm font-black">✓</span>
                        </div>
                      )}
                    </div>
                    {resume ? (
                      <div className="space-y-2 relative z-10">
                        <p className="text-lime-400 font-bold text-lg font-mono">[UPLOADED] {resume.name}</p>
                        <p className="text-gray-400 font-mono">Click to replace file</p>
                      </div>
                    ) : (
                      <div className="space-y-2 relative z-10">
                        <p className="text-white font-bold text-lg font-mono">DROP YOUR RESUME HERE</p>
                        <p className="text-gray-400 font-mono">or click to browse • PDF, DOC, DOCX</p>
                      </div>
                    )}
                    {/* Scan line effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-orange-400/20 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                  </div>
                </div>

                {/* Job Site URL */}
                <div className="space-y-4">
                  <label className="text-sm font-bold text-orange-400 uppercase tracking-widest font-mono flex items-center gap-2">
                    <span className="w-6 h-6 bg-orange-400 text-black rounded flex items-center justify-center text-xs font-black">
                      2
                    </span>
                    TARGET COORDINATES
                  </label>
                  <Input
                    type="url"
                    placeholder="https://target-corp.com/careers [ENTER INFILTRATION POINT]"
                    value={jobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                    className="h-16 text-lg bg-gray-800/50 border-gray-600 text-white placeholder-gray-500 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20 transition-all duration-300 font-mono"
                  />
                </div>

                {/* Launch Button */}
                <Button
                  onClick={handleSearch}
                  disabled={!resume || !jobUrl}
                  className="w-full h-20 text-xl font-black bg-gradient-to-r from-orange-500 via-red-500 to-orange-600 hover:from-orange-400 hover:via-red-400 hover:to-orange-500 text-white border-0 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-orange-500/25 disabled:transform-none disabled:opacity-50 disabled:cursor-not-allowed font-mono tracking-wider relative overflow-hidden group"
                >
                  <div className="flex items-center gap-4 relative z-10">
                    <Target className="h-8 w-8 animate-pulse" />
                    ROLL OUT
                    <Zap className="h-8 w-8 animate-pulse" />
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Loading State with Radar */}
        {isLoading && (
          <div className="fixed inset-0 bg-black/95 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in">
            <div className="text-center space-y-8">
              {/* Large Radar Display */}
              <div className="w-[600px] h-[600px] relative mx-auto">
                {/* Radar circles */}
                <div className="absolute inset-0 border-4 border-green-500 rounded-full opacity-80"></div>
                <div className="absolute inset-[12%] border-2 border-green-500 rounded-full opacity-60"></div>
                <div className="absolute inset-[24%] border-2 border-green-500 rounded-full opacity-60"></div>
                <div className="absolute inset-[36%] border-2 border-green-500 rounded-full opacity-60"></div>
                <div className="absolute inset-[48%] border-2 border-green-500 rounded-full opacity-60"></div>
                <div className="absolute inset-[60%] border-2 border-green-500 rounded-full opacity-60"></div>
                <div className="absolute inset-[72%] border-2 border-green-500 rounded-full opacity-60"></div>

                {/* Radar cross lines */}
                <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-green-500/70"></div>
                <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-green-500/70"></div>

                {/* Radar sweep - faster during loading */}
                <div
                  className="absolute top-1/2 left-1/2 w-[50%] h-1 bg-gradient-to-r from-green-500 to-transparent origin-left"
                  style={{
                    transform: `translateX(-2px) translateY(-2px) rotate(${radarAngle}deg)`,
                    boxShadow: "0 0 20px rgba(0, 255, 0, 0.9)",
                  }}
                ></div>

                {/* Anomaly blips during loading */}
                {anomalyBlips.map((blip) => (
                  <div
                    key={blip.id}
                    className={cn("absolute rounded-full animate-ping-slow", getBlipColor(blip.color))}
                    style={{
                      left: `${blip.x}%`,
                      top: `${blip.y}%`,
                      width: `${blip.size}px`,
                      height: `${blip.size}px`,
                      opacity: blip.opacity,
                      boxShadow: getBlipShadow(blip.color),
                    }}
                  ></div>
                ))}

                {/* Enhanced radar coordinates */}
                <div className="absolute top-2 left-2 text-green-500 text-sm font-mono">N 40°45'12.3"</div>
                <div className="absolute bottom-2 right-2 text-green-500 text-sm font-mono">E 73°58'44.1"</div>
                <div className="absolute top-2 right-2 text-green-500 text-sm font-mono">RANGE: 100KM</div>
                <div className="absolute bottom-2 left-2 text-green-500 text-sm font-mono">
                  ANOMALIES: {anomalyBlips.length}
                </div>

                {/* Status indicators */}
                <div className="absolute top-2 left-1/2 transform -translate-x-1/2 text-orange-400 text-sm font-mono animate-pulse">
                  [ACTIVE SCAN]
                </div>
                <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-red-400 text-sm font-mono animate-pulse">
                  [THREAT DETECTED]
                </div>
              </div>

              {/* Loading text under radar */}
              <div className="space-y-4">
                <h3 className="text-4xl font-black text-white font-mono tracking-wider">
                  {currentStep === "scanning" && "[SCANNING NETWORKS]"}
                  {currentStep === "infiltrating" && "[INFILTRATING SYSTEMS]"}
                  {currentStep === "calculating" && "[CALCULATING THREAT LEVELS]"}
                </h3>
                <p className="text-gray-400 text-lg font-mono">
                  {currentStep === "scanning" && "Probing target defenses and mapping entry points..."}
                  {currentStep === "infiltrating" && "Breaching firewalls and extracting job data..."}
                  {currentStep === "calculating" && "Analyzing compatibility and ranking opportunities..."}
                </p>
                <p className="text-orange-400 font-black text-2xl font-mono">[{progress}% COMPLETE]</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {searchComplete && jobs.length > 0 && (
          <div className="max-w-6xl mx-auto animate-fade-in">
            <div className="text-center mb-12">
              <h2 className="text-5xl font-black text-white mb-4 flex items-center justify-center gap-4 font-mono">
                <Target className="h-12 w-12 text-orange-400 animate-bounce" />
                [TARGETS ACQUIRED]
              </h2>
              <p className="text-xl text-gray-300 mb-8 font-mono">
                {jobs.length} HIGH-VALUE OPPORTUNITIES DETECTED • RANKED BY SURVIVAL PROBABILITY
              </p>
              <div className="flex justify-center gap-6">
                <Button
                  onClick={resetSearch}
                  variant="outline"
                  className="border-orange-400 text-orange-400 hover:bg-orange-400 hover:text-black transition-all duration-300 font-mono font-bold"
                >
                  NEW MISSION
                </Button>
                <Button className="bg-gradient-to-r from-lime-500 to-green-500 hover:from-lime-400 hover:to-green-400 text-black font-mono font-bold">
                  <Download className="h-4 w-4 mr-2" />
                  EXTRACT DATA
                </Button>
              </div>
            </div>

            <div className="grid gap-8">
              {jobs.map((job, index) => (
                <Card
                  key={job.id}
                  className="bg-gray-900/80 backdrop-blur-xl border-orange-600/30 hover:border-orange-400/60 transition-all duration-500 transform hover:-translate-y-2 hover:shadow-2xl hover:shadow-orange-500/20 group border-2"
                  style={{ animationDelay: `${index * 200}ms` }}
                >
                  <CardContent className="p-8">
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                      <div className="flex-1 space-y-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <div className="flex items-center gap-3">
                              <h3 className="text-2xl font-bold text-white group-hover:text-orange-400 transition-colors duration-300 font-mono">
                                {job.title}
                              </h3>
                              <Badge
                                className={cn(
                                  "text-xs font-bold px-2 py-1 border font-mono",
                                  getDifficultyColor(job.difficulty),
                                )}
                              >
                                {job.difficulty.toUpperCase()}
                              </Badge>
                            </div>
                            <p className="text-xl text-gray-300 font-bold font-mono">[{job.company}]</p>
                          </div>
                          <Badge
                            className={cn(
                              "text-lg font-black px-4 py-2 bg-gradient-to-r text-black border-0 font-mono",
                              getMatchColor(job.matchScore),
                            )}
                          >
                            {job.matchScore}% MATCH
                          </Badge>
                        </div>

                        <div className="flex flex-wrap items-center gap-6 text-gray-400 font-mono">
                          <div className="flex items-center gap-2">
                            <MapPin className="h-5 w-5 text-orange-400" />
                            <span className="font-bold">{job.location}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <DollarSign className="h-5 w-5 text-lime-400" />
                            <span className="font-bold">{job.salary}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Clock className="h-5 w-5 text-red-400" />
                            <span className="font-bold">{job.postedDate}</span>
                          </div>
                          <Badge variant="outline" className="border-gray-600 text-gray-300 font-mono font-bold">
                            {job.type}
                          </Badge>
                        </div>

                        <p className="text-gray-300 text-lg leading-relaxed font-mono">{job.description}</p>
                      </div>

                      <div className="flex flex-col items-center gap-4 lg:items-end">
                        <div className="text-center lg:text-right space-y-3">
                          <div className="flex items-center gap-3">
                            {renderHearts(job.matchScore)}
                            <div
                              className={cn(
                                "text-3xl font-black bg-gradient-to-r bg-clip-text text-transparent font-mono",
                                getMatchColor(job.matchScore),
                              )}
                            >
                              {job.matchScore}%
                            </div>
                          </div>
                          <div className="text-gray-400 font-bold font-mono">COMPATIBILITY</div>
                        </div>
                        <Button className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-400 hover:to-red-400 text-white font-black px-8 py-4 rounded-lg transition-all duration-300 transform hover:scale-105 font-mono tracking-wider">
                          GET THEM
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
