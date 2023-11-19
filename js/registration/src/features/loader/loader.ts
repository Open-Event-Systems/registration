import {
  ManagedLoaderComponentProps,
  createLoaderComponent,
} from "#src/features/loader/components"
import {
  Loader as LoaderType,
  ILoader,
  LoadedLoader,
  LoadingState,
} from "#src/features/loader/types"
import { action, makeObservable, observable, runInAction } from "mobx"
import { DependencyList, ElementType, useMemo } from "react"

class _NotFoundError extends Error {
  constructor(message = "Not found") {
    super(message)
  }
}

export const NotFoundError: {
  new (message?: string): Error
} = _NotFoundError

class Loader<T> implements ILoader<T> {
  state = LoadingState.notLoading
  value: T | null = null
  get ready() {
    return this.state == LoadingState.ready
  }

  Component: ElementType<ManagedLoaderComponentProps<T>>

  private loadFunc: () => T | Promise<T>
  private loadPromise: Promise<T> | undefined

  constructor(value: T | Promise<T> | (() => T | Promise<T>)) {
    if (typeof value == "function") {
      this.loadFunc = value as () => T | Promise<T>
    } else {
      this.loadFunc = () => value

      if (!isPromise(value)) {
        this.value = value
        this.state = LoadingState.ready
      }
    }

    this.Component = createLoaderComponent(this)

    makeObservable<this, "tryLoad">(this, {
      state: observable,
      value: observable.ref,
      tryLoad: action,
    })
  }

  load(): Promise<T> {
    if (!this.loadPromise) {
      this.loadPromise = this.tryLoad()
    }
    return this.loadPromise
  }

  private async tryLoad() {
    if (this.state == LoadingState.notLoading) {
      this.state = LoadingState.loading
    }
    try {
      const res = await this.loadFunc()
      runInAction(() => {
        this.value = res
        this.state = LoadingState.ready
      })
      return res
    } catch (e) {
      if (e instanceof NotFoundError) {
        runInAction(() => {
          this.state = LoadingState.notFound
        })
      }
      throw e
    }
  }

  then<TResult1 = T, TResult2 = never>(
    onfulfilled?:
      | ((value: T) => TResult1 | PromiseLike<TResult1>)
      | null
      | undefined,
    onrejected?:
      | ((reason: any) => TResult2 | PromiseLike<TResult2>)
      | null
      | undefined,
  ): Promise<TResult1 | TResult2> {
    return this.load().then(onfulfilled, onrejected)
  }

  catch<TResult = never>(
    onrejected?:
      | ((reason: any) => TResult | PromiseLike<TResult>)
      | null
      | undefined,
  ): Promise<T | TResult> {
    return this.load().catch(onrejected)
  }

  finally(onfinally?: (() => void) | null | undefined): Promise<T> {
    return this.load().finally(onfinally)
  }

  get [Symbol.toStringTag]() {
    return "[object Loader]"
  }
}

export function createLoader<T>(loadFunc: () => T | Promise<T>): LoaderType<T>
export function createLoader<T>(value: Promise<T>): LoaderType<T>
export function createLoader<T>(value: T): LoadedLoader<T>
export function createLoader<T>(
  loadFunc: (() => T | Promise<T>) | Promise<T> | T,
): ILoader<T> {
  return new Loader(loadFunc)
}

export function useLoader<T>(
  loadFunc: () => T | Promise<T>,
  deps: DependencyList,
): LoaderType<T>
export function useLoader<T>(
  value: Promise<T>,
  deps: DependencyList,
): LoaderType<T>
export function useLoader<T>(value: T, deps: DependencyList): LoadedLoader<T>
export function useLoader<T>(
  loadFunc: (() => T | Promise<T>) | Promise<T> | T,
  deps: DependencyList,
): ILoader<T> {
  return useMemo(() => new Loader(loadFunc), deps)
}

const isPromise = <T>(obj: unknown): obj is PromiseLike<T> =>
  typeof obj === "object" &&
  !!obj &&
  "then" in obj &&
  typeof obj.then == "function"
