import {
  Checkout,
  CheckoutExternalData,
  CheckoutResponse,
  CheckoutState,
} from "#src/features/checkout/types/Checkout"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import {
  QueryClient,
  QueryObserver,
  QueryObserverResult,
} from "@tanstack/react-query"
import { action, makeAutoObservable } from "mobx"

// class CheckoutImpl implements Checkout {
//   service: string
//   id: string
//   externalId: string
//   state: CheckoutState
//   data: CheckoutExternalData
//   error: string | null = null
//   observer: QueryObserver<CheckoutResponse>

//   private unsubscribe: () => void

//   constructor(
//     private api: CheckoutAPI,
//     private client: QueryClient,
//     public cartId: string,
//     public method: string | null,
//     response: CheckoutResponse,
//   ) {
//     this.service = response.service
//     this.id = response.id
//     this.externalId = response.external_id
//     this.state = response.state
//     this.data = response.data

//     this.observer = new QueryObserver(client, api.read(this.id))
//     this.unsubscribe = this.observer.subscribe(this.onUpdate)

//     makeAutoObservable(this)
//   }

//   private onUpdate = action((result: QueryObserverResult<CheckoutResponse>) => {
//     if (result.isSuccess) {
//       this.state = result.data.state
//       this.data = result.data.data

//       if (result.data.state == CheckoutState.canceled || result.data.state == CheckoutState.complete) {
//         this.unsubscribe()
//       }
//     }
//   })

//   async update(body?: Record<string, unknown>) {
//     await this.client.getMutationCache().build(this.client, this.api.update(this.id)).execute(body)
//     return null
//   }

//   async cancel() {
//     if (this.state == CheckoutState.canceled) {
//       return
//     } else if (this.state == CheckoutState.complete) {
//       // do nothing
//     } else {
//       await this.api.cancel(this.id)
//     }
//   }

// }
