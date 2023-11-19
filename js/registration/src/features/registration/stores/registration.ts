import { Registration } from "#src/features/registration"
import { makeAutoObservable } from "mobx"

export class RegistrationStore {
  constructor(public registration: Registration) {
    makeAutoObservable(this)
  }
}
