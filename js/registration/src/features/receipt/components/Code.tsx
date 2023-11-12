import clsx from "clsx"
import { ComponentPropsWithoutRef, useEffect, useState } from "react"
import QRCode from "qrcode"

export type ReceiptCodeProps = {
  receiptUrl: string
} & ComponentPropsWithoutRef<"img">

export const ReceiptCode = (props: ReceiptCodeProps) => {
  const { receiptUrl, className, ...other } = props

  const [dataURL, setDataURL] = useState<string | undefined>(undefined)

  useEffect(() => {
    makeCode(receiptUrl).then((dataURL) => {
      setDataURL(dataURL)
    })
  }, [receiptUrl])

  return (
    <img
      className={clsx(
        "ReceiptCode-root",
        { "ReceiptCode-loading": !dataURL },
        className,
      )}
      src={dataURL}
      alt=""
      {...other}
    />
  )
}

const makeCode = (url: string): Promise<string> => {
  const urlObj = new URL(url, window.location.href)
  const hostPart = `${urlObj.protocol}//${urlObj.host}`
  const pathParts = urlObj.pathname.split("/")
  const pathPrefix = pathParts.slice(0, pathParts.length - 1).join("/") + "/"
  const id = pathParts[pathParts.length - 1]
  const fragment = urlObj.hash
  return QRCode.toDataURL([
    {
      data: hostPart.toUpperCase(),
      mode: "alphanumeric",
    },
    {
      data: pathPrefix,
    },
    {
      data: id.toUpperCase(),
      mode: "alphanumeric",
    },
    ...(fragment ? [{ data: fragment }] : []),
  ])
}
