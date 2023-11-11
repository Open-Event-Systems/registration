import { ShowLoadingOverlay } from "#src/components"
import { SimpleLayout } from "#src/components/layout/SimpleLayout"
import { AuthStoreProvider } from "#src/features/auth/providers"
import { WretchContext } from "#src/hooks/api"
import { AppStoreContext } from "#src/hooks/app"
import { useLoader } from "#src/hooks/loader"
import { NotFoundPage } from "#src/routes/NotFoundPage"
import { AppStore } from "#src/stores/AppStore"
import { ReactNode } from "react"

export const AppProvider = ({ children }: { children?: ReactNode }) => {
  const appStoreLoader = useLoader(async () => {
    const app = await AppStore.fromConfig()
    return app
  })

  return (
    <appStoreLoader.Component
      notFound={
        <SimpleLayout>
          <NotFoundPage />
        </SimpleLayout>
      }
      placeholder={<ShowLoadingOverlay />}
    >
      {(appStore) => (
        <AppStoreContext.Provider value={appStore}>
          <AuthStoreProvider authStore={appStore.authStore}>
            <WretchContext.Provider value={appStore.authStore.authWretch}>
              {children}
            </WretchContext.Provider>
          </AuthStoreProvider>
        </AppStoreContext.Provider>
      )}
    </appStoreLoader.Component>
  )
}
