export function AttachmentElement(props: {
    id: string,
    name: string
}) {
    return(
        <span id={props.id}>{props.name}</span>
    )
}