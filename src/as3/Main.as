package
{
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Rectangle;

	import lesta.api.ModBase;

	/**
	 * Flash-Teil der Standalone-Fassung: Greifflaeche zum Verschieben der Anzeige per Maus.
	 *
	 * Offizielle ModsAPI (FlashAPI): gameAPI.stage fuer die Flaeche, gameAPI.data als Kanal zu
	 * Main.py. Die Anzeige selbst bleibt in Overmatcher.unbound; diese Flaeche liegt unsichtbar
	 * darueber, zeigt beim Ueberfahren einen feinen Rahmen und meldet beim Ziehen den Abstand der
	 * linken oberen Ecke zur Bildschirmmitte:
	 *   Python -> Flash  omSetHandle [x, y, breite, hoehe, aktiv]  (x/y relativ zur Mitte)
	 *   Flash -> Python  omDragMove  [x, y]  waehrend des Ziehens
	 *                    omDragEnd   [x, y]  beim Loslassen (wird gespeichert)
	 * Gebaut mit tools/build_flash.py (Apache Flex SDK, wows_library.swc aus dem ModSDK).
	 */
	public class Main extends ModBase
	{
		private var handle:Sprite;
		private var handleWidth:Number = 62;
		private var handleHeight:Number = 29;
		private var offsetX:Number = 30;
		private var offsetY:Number = 8;
		private var active:Boolean = false;
		private var dragging:Boolean = false;
		private var hover:Boolean = false;
		private var stageW:Number = 0;
		private var stageH:Number = 0;

		public function Main()
		{
			super();
		}

		override public function init():void
		{
			super.init();
			handle = new Sprite();
			handle.buttonMode = true;
			handle.visible = false;
			handle.addEventListener(MouseEvent.MOUSE_DOWN, onDown);
			handle.addEventListener(MouseEvent.ROLL_OVER, onOver);
			handle.addEventListener(MouseEvent.ROLL_OUT, onOut);
			gameAPI.stage.addChild(handle);
			gameAPI.data.addCallBack("omSetHandle", onSetHandle);
			redraw();
		}

		override public function fini():void
		{
			stopDragging(false);
			if (handle != null)
			{
				gameAPI.stage.removeChild(handle);
				handle = null;
			}
			super.fini();
		}

		override public function updateStage(width:Number, height:Number):void
		{
			super.updateStage(width, height);
			stageW = width;
			stageH = height;
			place();
		}

		private function onSetHandle(x:Number, y:Number, w:Number, h:Number, isActive:Boolean):void
		{
			if (!dragging)
			{
				offsetX = x;
				offsetY = y;
			}
			handleWidth = Math.max(w, 8);
			handleHeight = Math.max(h, 8);
			active = isActive;
			if (!active)
			{
				stopDragging(false);
			}
			redraw();
			place();
		}

		private function place():void
		{
			if (handle == null || dragging)
			{
				return;
			}
			handle.x = stageW / 2 + offsetX;
			handle.y = stageH / 2 + offsetY;
			handle.visible = active;
		}

		private function redraw():void
		{
			if (handle == null)
			{
				return;
			}
			handle.graphics.clear();
			// Fuellung mit Deckkraft 0 ist unsichtbar, nimmt aber Mausereignisse an
			handle.graphics.beginFill(0x000000, 0);
			handle.graphics.drawRect(0, 0, handleWidth, handleHeight);
			handle.graphics.endFill();
			if (hover || dragging)
			{
				handle.graphics.lineStyle(1, 0xFFFFFF, 0.45);
				handle.graphics.drawRect(-1, -1, handleWidth + 1, handleHeight + 1);
			}
		}

		private function onOver(event:MouseEvent):void
		{
			hover = true;
			redraw();
		}

		private function onOut(event:MouseEvent):void
		{
			hover = false;
			redraw();
		}

		private function onDown(event:MouseEvent):void
		{
			if (!active)
			{
				return;
			}
			dragging = true;
			// nicht ueber den Bildschirmrand hinaus
			handle.startDrag(false, new Rectangle(0, 0, Math.max(stageW - handleWidth, 0), Math.max(stageH - handleHeight, 0)));
			handle.stage.addEventListener(MouseEvent.MOUSE_MOVE, onMove);
			handle.stage.addEventListener(MouseEvent.MOUSE_UP, onUp);
			redraw();
		}

		private function onMove(event:MouseEvent):void
		{
			gameAPI.data.call("omDragMove", currentOffset());
		}

		private function onUp(event:MouseEvent):void
		{
			stopDragging(true);
		}

		private function stopDragging(report:Boolean):void
		{
			if (!dragging || handle == null)
			{
				return;
			}
			handle.stopDrag();
			if (handle.stage != null)
			{
				handle.stage.removeEventListener(MouseEvent.MOUSE_MOVE, onMove);
				handle.stage.removeEventListener(MouseEvent.MOUSE_UP, onUp);
			}
			dragging = false;
			var pos:Array = currentOffset();
			offsetX = pos[0];
			offsetY = pos[1];
			if (report)
			{
				gameAPI.data.call("omDragEnd", pos);
			}
			redraw();
		}

		private function currentOffset():Array
		{
			return [Math.round(handle.x - stageW / 2), Math.round(handle.y - stageH / 2)];
		}
	}
}
