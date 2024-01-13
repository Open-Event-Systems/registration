import { Search } from "#src/features/checkout/components/search/Search"
import { useCheckoutAPI } from "#src/features/checkout/hooks"
import { useNavigate } from "#src/hooks/location"
import { useQuery } from "@tanstack/react-query"
import { action, observable } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { useEffect } from "react"

export const CheckoutSearchPage = observer(() => {
  const navigate = useNavigate()

  const searchState = useLocalObservable(
    () => ({
      current: {
        query: "",
        showAll: false,
      },
      throttled: {
        query: "",
        showAll: false,
      },
    }),
    {
      current: observable.ref,
      throttled: observable.ref,
    },
  )

  const checkoutAPI = useCheckoutAPI()
  const searchQuery = useQuery({
    ...checkoutAPI.list(searchState.throttled.query, {
      showAll: searchState.throttled.showAll,
    }),
    placeholderData(prev) {
      if (searchState.throttled.query) {
        return prev
      } else {
        return
      }
    },
    enabled: !!searchState.throttled.query,
  })

  useEffect(() => {
    const cur = searchState.current

    const timeout = window.setTimeout(
      action(() => {
        searchState.throttled = {
          query: cur.query.trim(),
          showAll: cur.showAll,
        }
      }),
      250,
    )

    return () => {
      window.clearTimeout(timeout)
    }
  }, [searchState.current])

  return (
    <Search
      value={searchState.current.query}
      showAll={searchState.current.showAll}
      onChange={action((v) => {
        searchState.current = v
      })}
      results={searchQuery.data}
      getLink={(row) => {
        if (row.cart_id) {
          return `/checkouts/cart/${row.cart_id}`
        } else {
          return
        }
      }}
      onSelect={(row) => {
        if (row.cart_id) {
          navigate(`/checkouts/cart/${row.cart_id}`)
        }
      }}
    />
  )
})

CheckoutSearchPage.displayName = "CheckoutSearchPage"
