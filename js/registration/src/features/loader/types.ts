export enum LoadingState {
  notLoading = "notLoading",
  loading = "loading",
  rejected = "rejected",
  resolved = "resolved",
}

type ValueOrPromise<T> = T | Promise<T>
type LoadFunc<T> = () => ValueOrPromise<T>
export type LoadValue<T> = LoadFunc<T> | ValueOrPromise<T>

export interface ILoader<T> extends Promise<T> {
  get state(): LoadingState
  get value(): T | null
  get error(): unknown
  get ready(): boolean

  load(): Promise<T>
}

export interface PendingLoader<T> extends ILoader<T> {
  get state(): LoadingState.loading | LoadingState.notLoading
  get value(): never
  get error(): null
  get ready(): false
}

export interface RejectedLoader<T> extends ILoader<T> {
  get state(): LoadingState.rejected
  get value(): never
  get error(): unknown
  get ready(): true
}

export interface ResolvedLoader<T> extends ILoader<T> {
  get state(): LoadingState.resolved
  get value(): T
  get error(): null
  get ready(): true
}

export type Loader<T> = PendingLoader<T> | ResolvedLoader<T> | RejectedLoader<T>
