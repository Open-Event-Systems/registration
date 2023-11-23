import {
  action,
  autorun,
  makeAutoObservable,
  observable,
  runInAction,
} from "mobx"
import { observer } from "mobx-react-lite"
import { IObservableValue } from "mobx"
import {
  ReactNode,
  createContext,
  useContext,
  useLayoutEffect,
  useState,
} from "react"

class TitleState {
  title: IObservableValue<string>[] = []
  subtitle: IObservableValue<string>[] = []

  constructor() {
    makeAutoObservable(this)

    autorun(() => {
      if (this.title.length > 0) {
        const title = this.title[this.title.length - 1]
        document.title = title.get()
      }
    })
  }
}

export const TitlePlaceholder = observer(() => {
  const state = useContext(TitleContext)

  let title
  if (state.title.length > 0) {
    title = state.title[state.title.length - 1]?.get()
  }

  return <>{title}</>
})

export const SubtitlePlaceholder = observer(() => {
  const state = useContext(TitleContext)

  let subtitle
  if (state.subtitle.length > 0) {
    subtitle = state.subtitle[state.subtitle.length - 1]?.get()
  }

  return <>{subtitle}</>
})

export const Title = ({
  children,
  title,
}: {
  children?: ReactNode
  title: string
}) => {
  const state = useContext(TitleContext)
  const [localState] = useState(() => observable.box(title))

  useLayoutEffect(() => {
    runInAction(() => {
      state.title.push(localState)
    })

    return action(() => {
      state.title.pop()
    })
  }, [])

  useLayoutEffect(() => {
    runInAction(() => {
      localState.set(title)
    })
  }, [title])

  return <>{children}</>
}

export const Subtitle = ({
  children,
  subtitle,
}: {
  children?: ReactNode
  subtitle: string
}) => {
  const state = useContext(TitleContext)
  const [localState] = useState(() => observable.box(subtitle))

  useLayoutEffect(() => {
    runInAction(() => {
      state.subtitle.push(localState)
    })

    return action(() => {
      state.subtitle.pop()
    })
  }, [])

  useLayoutEffect(() => {
    runInAction(() => {
      localState.set(subtitle)
    })
  }, [subtitle])

  return <>{children}</>
}

export const TitleContext = createContext(new TitleState())
