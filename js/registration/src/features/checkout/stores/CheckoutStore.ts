import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { makeAutoObservable } from "mobx"

export class CheckoutStore {
  constructor(private api: CheckoutAPI) {
    makeAutoObservable(this)
  }
}
