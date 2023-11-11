import {
  DefaultProps,
  MantineTheme,
  MantineThemeOverride,
  Styles,
} from "@mantine/core"

import { CartProps } from "#src/features/cart/components/Cart"
import { LineItemProps } from "#src/features/cart/components/cart/LineItem"
import { ModifierProps } from "#src/features/cart/components/cart/Modifier"
import { CardGridProps } from "#src/features/selfservice/components/card/CardGrid"
import { RegistrationCardProps } from "#src/features/selfservice/components/card/RegistrationCard"
import { LoadingOverlayProps } from "#src/routes/LoadingOverlay"
import { AppShellLayoutProps } from "#src/components/layout/AppShellLayout"
import { ContainerLayoutProps } from "#src/components/layout/ContainerLayout"
import { HeaderProps } from "#src/components/layout/Header"
import { StackLayoutProps } from "#src/components/layout/StackLayout"
import { TitleAreaProps } from "#src/components/layout/TitleArea"
import { SigninDialogProps } from "#src/features/auth/components/SigninDialog"
import { CheckoutDialogProps } from "#src/features/checkout/components/checkout/CheckoutDialog"
import { LogoProps } from "#src/components/layout/Logo"
import {
  ButtonListButtonProps,
  ButtonListDividerProps,
  ButtonListLabelProps,
  ButtonListProps,
} from "#src/components/button-list/ButtonList"
import { ModalDialogProps } from "#src/components/dialog/ModalDialog"
import { EmailAuthProps } from "#src/features/auth/components/signin/EmailAuth"

interface Components {
  // src/components
  ButtonList: ButtonListProps
  ButtonListButton: ButtonListButtonProps
  ButtonListLabel: ButtonListLabelProps
  ButtonListDivider: ButtonListDividerProps
  ModalDialog: ModalDialogProps
  AppShellLayout: AppShellLayoutProps
  ContainerLayout: ContainerLayoutProps
  Header: HeaderProps
  Logo: LogoProps
  StackLayout: StackLayoutProps
  TitleArea: TitleAreaProps

  // src/features/auth/components
  EmailAuth: EmailAuthProps
  SigninDialog: SigninDialogProps

  // src/features/cart/components
  Cart: CartProps
  LineItem: LineItemProps
  Modifier: ModifierProps

  // src/features/checkout/components
  CheckoutDialog: CheckoutDialogProps

  // src/features/selfservice/components
  CardGrid: CardGridProps
  RegistrationCard: RegistrationCardProps

  // src/routes
  LoadingOverlay: LoadingOverlayProps
}

interface ThemeComponentOf<Props> {
  defaultProps?: Partial<Props> | ((theme: MantineTheme) => Partial<Props>)
  classNames?: Record<string, string>
  styles?: Props extends DefaultProps<infer C, infer P>
    ? Styles<C, P>
    : Styles<string>
}

type ThemeComponents = {
  [C in keyof Components]?: ThemeComponentOf<Components[C]>
} & MantineTheme["components"]

export type ThemeOverride = MantineThemeOverride & {
  components?: ThemeComponents
}
