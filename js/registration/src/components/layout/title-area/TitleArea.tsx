import { Logo, LogoProps } from "#src/components/layout/logo/Logo"
import {
  SubtitlePlaceholder,
  TitlePlaceholder,
} from "#src/components/title/Title"
import {
  Box,
  BoxProps,
  Container,
  ContainerProps,
  Text,
  TextProps,
  Title,
  TitleProps,
  useProps,
} from "@mantine/core"
import clsx from "clsx"

export type TitleAreaProps = {
  noLogo?: boolean
  LogoProps?: LogoProps
  TitleProps?: TitleProps
  SubtitleProps?: TextProps
  ContainerProps?: ContainerProps
} & BoxProps

export const TitleArea = (props: TitleAreaProps) => {
  const {
    className,
    noLogo,
    LogoProps,
    TitleProps,
    SubtitleProps,
    ContainerProps,
    ...other
  } = useProps("TitleArea", {}, props)

  return (
    <Box className={clsx("TitleArea-root", className)} {...other}>
      <Container className="TitleArea-container" size="lg" {...ContainerProps}>
        {!noLogo && <Logo className="TitleArea-logo" {...LogoProps} />}
        <Title order={1} className="TitleArea-title" {...TitleProps}>
          <TitlePlaceholder />
        </Title>
        <Text className="TitleArea-subtitle" {...SubtitleProps}>
          <SubtitlePlaceholder />
        </Text>
      </Container>
    </Box>
  )
}
