import {
  Loader as LoaderType,
  ILoader,
  ResolvedLoader,
  LoadingState,
  LoadValue,
} from "#src/features/loader/types"
import { action, makeObservable, observable, runInAction } from "mobx"
import { DependencyList, useMemo } from "react"

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
  error: unknown = null

  private _value: T | null = null
  private loadFunc: () => Promise<T>
  private loadPromise: Promise<T> | null = null

  get value(): T {
    if (this.state == LoadingState.resolved) {
      return this._value as T
    } else if (this.state == LoadingState.rejected) {
      throw this.error
    } else {
      throw this
    }
  }

  get ready() {
    return this.state == LoadingState.resolved
  }

  constructor(value: LoadValue<T>) {
    if (typeof value == "function") {
      this.loadFunc = () => Promise.resolve((value as () => T | Promise<T>)())
    } else if (isPromise(value)) {
      this.loadFunc = () => value
      this.state = LoadingState.loading
    } else {
      this.loadFunc = () => Promise.resolve(value)
      this._value = value
      this.state = LoadingState.resolved
    }

    makeObservable<this, "tryLoad">(this, {
      state: observable,
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
        this._value = res
        this.state = LoadingState.resolved
      })
      return res
    } catch (e) {
      runInAction(() => {
        this.state = LoadingState.rejected
        this.error = e
      })
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

  [Symbol.toStringTag] = "[object Loader]"
}

export function createLoader<T>(loadFunc: () => Promise<T>): LoaderType<T>
export function createLoader<T>(loadFunc: () => T): LoaderType<T>
export function createLoader<T>(promise: Promise<T>): LoaderType<T>
export function createLoader<T>(value: T): ResolvedLoader<T>
export function createLoader<T>(loadValue: LoadValue<T>): ILoader<T> {
  if (loadValue instanceof Loader) {
    return loadValue
  } else {
    return new Loader(loadValue)
  }
}

export function useLoader<T>(
  loadFunc: () => Promise<T>,
  deps: DependencyList,
): LoaderType<T>
export function useLoader<T>(
  loadFunc: () => T,
  deps: DependencyList,
): LoaderType<T>
export function useLoader<T>(
  value: Promise<T>,
  deps: DependencyList,
): LoaderType<T>
export function useLoader<T>(value: T, deps: DependencyList): ResolvedLoader<T>
export function useLoader<T>(
  loadValue: LoadValue<T>,
  deps: DependencyList,
): ILoader<T> {
  return useMemo(() => createLoader(loadValue), deps) as ILoader<T>
}

const isPromise = <T>(t: unknown): t is Promise<T> =>
  !!t && typeof t == "object" && "then" in t && typeof t.then == "function"
