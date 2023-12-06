import { Box, Text } from "@mantine/core"
import { useEffect, useState } from "react"
import QRCode from "qrcode"

export type DeviceAuthRequestProps = {
  url: string
  urlComplete: string
  userCode: string
}

export const DeviceAuthRequest = (props: DeviceAuthRequestProps) => {
  const { url, urlComplete, userCode } = props

  const [dataURL, setDataURL] = useState<string | undefined>(undefined)

  useEffect(() => {
    QRCode.toDataURL(urlComplete, { width: 200 }).then((dataURL) =>
      setDataURL(dataURL),
    )
  }, [url])

  return (
    <Box className="DeviceAuthRequest-root">
      <Text className="DeviceAuthRequest-text" c="dimmed" fz="smaller">
        Scan code
      </Text>
      <img className={"DeviceAuthRequest-qrCode"} src={dataURL} alt="" />
      <Text className="DeviceAuthRequest-text" c="dimmed" fz="smaller">
        or visit
        <br />
        {url}
        <br />
        and enter code{" "}
        <Text component="code" fw="bold">
          {String(userCode)}
        </Text>
      </Text>
    </Box>
  )
}
