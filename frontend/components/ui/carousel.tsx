"use client"

import * as React from "react"
import useEmblaCarousel, {
  type UseEmblaCarouselType,
} from "embla-carousel-react"
import ArrowLeft from "lucide-react/dist/esm/icons/arrow-left.js"
import ArrowRight from "lucide-react/dist/esm/icons/arrow-right.js"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

type CarouselApi = UseEmblaCarouselType[1]
type UseCarouselParameters = Parameters<typeof useEmblaCarousel>
type CarouselOptions = UseCarouselParameters[0]
type CarouselPlugin = UseCarouselParameters[1]

type CarouselProps = {
  opts?: CarouselOptions
  plugins?: CarouselPlugin
  orientation?: "horizontal" | "vertical"
  setApi?: (api: CarouselApi) => void
}

type CarouselContextProps = {
  carouselRef: ReturnType<typeof useEmblaCarousel>[0]
  api: CarouselApi | null | undefined
  scrollPrev: () => void
  scrollNext: () => void
  canScrollPrev: boolean
  canScrollNext: boolean
} & CarouselProps

const CarouselContext = React.createContext<CarouselContextProps | null>(null)

function useCarousel() {
  const context = React.useContext(CarouselContext)

  if (!context) {
    throw new Error("useCarousel must be used within a <Carousel />")
  }

  return context
}

const Carousel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & CarouselProps
>(
  (
    {
      orientation = "horizontal",
      opts,
      plugins,
      setApi,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const [viewportRef, embla] = useEmblaCarousel(opts, plugins)
    const apiRef = React.useRef<CarouselApi>(null)
    const onInit = React.useCallback(
      (api: CarouselApi) => {
        apiRef.current = api

        if (typeof setApi === "function") {
          setApi(api)
        }
      },
      [setApi]
    )

    const scrollPrev = React.useCallback(() => {
      if (!embla) return

      embla.scrollPrev()
    }, [embla])

    const scrollNext = React.useCallback(() => {
      if (!embla) return

      embla.scrollNext()
    }, [embla])

    const scrollTo = React.useCallback(
      (index: number) => {
        if (!embla) return

        embla.scrollTo(index)
      },
      [embla]
    )

    const { current: api } = apiRef

    React.useEffect(() => {
      if (!embla) return

      onInit(embla)
    }, [embla, onInit])

    const canScrollPrev = !!(api && api.canScrollPrev())
    const canScrollNext = !!(api && api.canScrollNext())

    const contextValue = React.useMemo(
      () => ({
        carouselRef: viewportRef,
        api,
        scrollPrev,
        scrollNext,
        canScrollPrev,
        canScrollNext,
        opts,
        plugins,
        orientation,
        setApi,
      }),
      [
        api,
        canScrollNext,
        canScrollPrev,
        orientation,
        plugins,
        opts,
        scrollNext,
        scrollPrev,
        setApi,
        viewportRef,
      ]
    )

    return (
      <CarouselContext.Provider value={contextValue}>
        <div
          ref={ref}
          className={cn("embla", orientation === "vertical" && "embla--vertical", className)}
          {...props}
        >
          <div className="embla__viewport" ref={viewportRef}>
            <div className="embla__container">{children}</div>
          </div>
          {canScrollPrev && (
            <Button
              variant="ghost"
              className="embla__prev"
              onClick={scrollPrev}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
          )}
          {canScrollNext && (
            <Button
              variant="ghost"
              className="embla__next"
              onClick={scrollNext}
            >
              <ArrowRight className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CarouselContext.Provider>
    )
  }
)

Carousel.displayName = "Carousel"

export { Carousel, useCarousel }
