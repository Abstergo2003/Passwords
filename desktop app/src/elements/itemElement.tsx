import "../styles/itemElement.css"

function ItemElement(props: {
    item: {},
    image: string
}) {

    console.log(props.item)
    return(
        <div className="item">
            <img src={props.image} />
            <span>lol</span>
            <span>lol</span>
        </div>
    )
}

export default ItemElement