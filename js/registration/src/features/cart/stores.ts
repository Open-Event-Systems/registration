import {
  fetchCart,
  fetchCartInterview,
  fetchEmptyCart,
  removeRegistrationFromCart,
} from "#src/features/cart/api"
import { Cart } from "#src/features/cart/types"
import { getCurrentCartId, setCurrentCartId } from "#src/features/cart/utils"
import { isNotFoundError } from "#src/utils/api"
import { Loader, createLoader } from "#src/utils/loader"
import {
  InterviewRecordStore,
  InterviewStateRecord,
  defaultAPI,
  startInterview,
} from "@open-event-systems/interview-lib"
import { makeAutoObservable, reaction, runInAction } from "mobx"
import { Wretch } from "wretch"

export class CartStore {
  loaders = new Map<string, Loader<Cart>>()

  constructor(
    public wretch: Wretch,
    public interviewRecordStore: InterviewRecordStore,
  ) {
    makeAutoObservable(this)
  }

  getCart(id: string): Cart | undefined {
    const loader = this.loaders.get(id)
    if (loader?.checkLoaded()) {
      return loader.value
    } else {
      return undefined
    }
  }

  load(id: string): Loader<Cart> {
    let loader = this.loaders.get(id)
    if (!loader) {
      loader = createLoader(() => fetchCart(this.wretch, id))
      this.loaders.set(id, loader)
    }

    return loader
  }

  async removeRegistrationFromCart(
    cartId: string,
    registrationId: string,
  ): Promise<[string, Cart]> {
    const [id, cart] = await removeRegistrationFromCart(
      this.wretch,
      cartId,
      registrationId,
    )
    runInAction(() => {
      this.loaders.set(
        id,
        createLoader(async () => cart),
      )
    })
    return [id, cart]
  }

  /**
   * Start a new interview with a cart.
   * @param cartId - The cart ID.
   * @param cart - The cart data.
   * @param interviewId - The interview ID.
   * @param registrationId - The registration ID.
   * @param accessCode - An access code.
   * @returns A new {@link InterviewStateRecord}.
   */
  async startInterviewForCart(
    cartId: string,
    cart: Cart,
    interviewId: string,
    registrationId?: string,
    accessCode?: string,
  ): Promise<InterviewStateRecord> {
    const res = await fetchCartInterview(
      this.wretch,
      cartId,
      interviewId,
      registrationId,
      accessCode,
    )

    return await startInterview(this.interviewRecordStore, defaultAPI, res, {
      cartId: cartId,
      eventId: cart.event_id,
    })
  }

  /**
   * Start a new interview. Checks and sets the current cart.
   * @param currentCart - A {@link CurrentCartStore}.
   * @param interviewId - The interview ID.
   * @param registrationId - The registration ID.
   * @param accessCode - An access code.
   * @returns A new {@link InterviewStateRecord}.
   */
  async startInterview(
    currentCart: CurrentCartStore,
    interviewId: string,
    registrationId?: string,
    accessCode?: string,
  ): Promise<InterviewStateRecord> {
    const [cartId, cart] = await currentCart.checkAndSetCurrentCart()
    return await this.startInterviewForCart(
      cartId,
      cart,
      interviewId,
      registrationId,
      accessCode,
    )
  }
}

export class CurrentCartStore {
  currentCartId: string | null
  loader: Loader<Cart> | null = null

  constructor(
    public wretch: Wretch,
    public eventId: string,
    public cartStore: CartStore,
  ) {
    this.currentCartId = getCurrentCartId() ?? null
    makeAutoObservable(this)

    reaction(
      () => this.currentCartId,
      (cartId) => {
        if (cartId) {
          setCurrentCartId(cartId)
        }
      },
    )
  }

  /**
   * Fetch the current cart by ID. Returns null if not found or if it does not match the
   * event.
   * @returns The current {@link Cart}, or null.
   */
  async checkCurrentCart(): Promise<Cart | null> {
    const id = this.currentCartId
    if (!id) {
      return null
    }

    try {
      const cart = await this.cartStore.load(id)

      if (cart.event_id != this.eventId) {
        return null
      }
      return cart
    } catch (e) {
      if (isNotFoundError(e)) {
        return null
      }
      throw e
    }
  }

  /**
   * Check that the current cart exists and matches the current event. If not, fetch the
   * empty cart and update the stored current cart ID.
   */
  async checkAndSetCurrentCart(): Promise<[string, Cart]> {
    const curId = this.currentCartId
    const cur = await this.checkCurrentCart()
    if (cur) {
      runInAction(() => {
        this.loader = createLoader(async () => cur, cur)
      })
      return [curId as string, cur]
    }

    const [emptyId, empty] = await fetchEmptyCart(this.wretch, this.eventId)
    runInAction(() => {
      this.currentCartId = emptyId
      this.loader = createLoader(async () => empty, empty)
    })
    return [emptyId, empty]
  }

  /**
   * Clear the current cart.
   */
  clearCurrentCart() {
    this.currentCartId = null
    setCurrentCartId("")
    this.checkAndSetCurrentCart()
  }

  /**
   * Set the current cart ID.
   * @param id - The cart ID.
   * @param value - The cart, or loader for the cart.
   */
  setCurrentCart(id: string, value?: Cart | Loader<Cart>) {
    this.currentCartId = id

    if (value && "load" in value) {
      this.loader = value
    } else if (value) {
      this.loader = createLoader(async () => value, value)
    }
  }
}
