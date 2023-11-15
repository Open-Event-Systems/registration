import { ManagedLoaderComponentProps } from "#src/features/loader/components"
import { ElementType } from "react"

export enum LoadingState {
  notLoading = "notLoading",
  loading = "loading",
  notFound = "notFound",
  ready = "ready",
}

export interface ILoader<T> extends Promise<T> {
  get state(): LoadingState
  get value(): T | undefined
  get ready(): boolean
  get Component(): ElementType<ManagedLoaderComponentProps<T>>

  load(): Promise<T>
}

export interface UnloadedLoader<T> extends ILoader<T> {
  get state(): Exclude<LoadingState, LoadingState.ready>
  get value(): undefined
  get ready(): false
}

export interface LoadedLoader<T> extends ILoader<T> {
  get state(): LoadingState.ready
  get value(): T
  get ready(): true
}

export type Loader<T> = UnloadedLoader<T> | LoadedLoader<T>
