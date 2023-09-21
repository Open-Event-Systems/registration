import { signInOptions } from "#src/features/auth/signInOptions.js"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import { AuthStore } from "#src/features/auth/stores/AuthStore.js"
import {
  SignInOptionComponentProps,
  SignInOption,
  SignInState,
} from "#src/features/auth/types/SignInOptions.js"
import { makeAutoObservable, runInAction } from "mobx"
import { ReactNode } from "react"
import { Wretch } from "wretch"

export class SignInStore implements SignInState {
  /**
   * Whether initial setup has finished.
   */
  ready = false

  /**
   * Loading state
   */
  loading = false

  webAuthnError = false

  options: SignInOption[] = []

  selectedOptionRender:
    | ((props: SignInOptionComponentProps) => ReactNode)
    | null = null

  setLoading(loading: boolean) {
    this.loading = loading
  }

  setWebAuthnError() {
    this.webAuthnError = true
  }

  handleComplete(authInfo: AuthInfo) {
    this.authStore.authInfo = authInfo
  }

  constructor(public wretch: Wretch, private authStore: AuthStore) {
    makeAutoObservable(this)
  }

  async load() {
    await this.loadOptions()
    runInAction(() => {
      this.ready = true
    })
  }

  private async loadOptions() {
    const results = await Promise.all(
      Object.values(signInOptions).map((opt) => opt(this.wretch, this))
    )
    const allowed = results.filter((opt): opt is SignInOption => !!opt)
    runInAction(() => {
      this.options = allowed
    })
    return allowed
  }

  async selectOption(option: SignInOption) {
    this.selectedOptionRender = null
    const result = await option.getRender()
    if (typeof result == "function") {
      runInAction(() => {
        this.selectedOptionRender = result
      })
    } else if (result) {
      this.handleComplete(result)
    }
    return result
  }
}
