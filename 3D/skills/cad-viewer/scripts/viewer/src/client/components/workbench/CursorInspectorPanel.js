import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronDown, ChevronUp, Copy, Pin } from "lucide-react";

import { copyTextToClipboard } from "@/ui/clipboard";
import { cn } from "@/ui/utils";
import { inspectorReadoutRefToken, serializeInspectorReadout } from "@/workbench/inspectorReadout";
import { Button } from "../ui/button";

const SURFACE_CLASS = "cad-glass-surface border border-sidebar-border text-sidebar-foreground shadow-sm";
const MAX_SNAPSHOTS = 3;
const SNAPSHOT_TTL_MS = 10_000;
// Each axis sits in a fixed-width slot (sign + up to 3 digits) so the live value never shifts the
// parentheses/commas around it — only the digits change, right-aligned, in place.
const COORD_SLOT_STYLE = { width: "4ch" };

function CoordSlot({ value }) {
  const numeric = Number(value);
  const rounded = Number.isFinite(numeric) ? Math.round(numeric) : null;
  const text = rounded === null ? "—" : String(Object.is(rounded, -0) ? 0 : rounded);
  return <span className="inline-block text-right" style={COORD_SLOT_STYLE}>{text}</span>;
}

function CursorValue({ xyz }) {
  if (!Array.isArray(xyz) || xyz.length < 3) {
    return <span className="font-mono text-[11px] tabular-nums">—</span>;
  }
  return (
    <span className="whitespace-nowrap font-mono text-[11px] tabular-nums">
      (<CoordSlot value={xyz[0]} />,{" "}<CoordSlot value={xyz[1]} />,{" "}<CoordSlot value={xyz[2]} />) mm
    </span>
  );
}

function FieldRows({ fields }) {
  if (!Array.isArray(fields) || !fields.length) {
    return null;
  }
  return (
    <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-0.5">
      {fields.map((item) => (
        <div key={item.key} className="contents">
          <dt className="text-[10px] uppercase tracking-[0.08em] text-muted-foreground">{item.label}</dt>
          <dd className="text-right font-mono text-[11px] tabular-nums">
            {item.value}{item.unit ? ` ${item.unit}` : ""}
          </dd>
        </div>
      ))}
    </dl>
  );
}

function ReadoutBody({ readout }) {
  const entity = readout?.entity || null;
  return (
    <div className="space-y-1.5">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-[10px] uppercase tracking-[0.08em] text-muted-foreground">Cursor</span>
        <CursorValue xyz={readout?.cursor?.xyz} />
      </div>
      {entity ? (
        <div className="space-y-1 border-t border-sidebar-border/60 pt-1.5">
          <div className="flex items-center justify-between gap-2">
            <span className="truncate font-medium">{entity.label}</span>
            <span className="shrink-0 rounded bg-sidebar-accent px-1.5 py-0.5 text-[10px] text-sidebar-accent-foreground">
              {entity.subtype}
            </span>
          </div>
          {entity.occurrence?.name ? (
            <div className="truncate text-[10px] text-muted-foreground">in {entity.occurrence.name}</div>
          ) : null}
          {entity.refToken ? (
            <div className="truncate font-mono text-[10px] text-muted-foreground">{entity.refToken}</div>
          ) : null}
          <FieldRows fields={entity.fields} />
        </div>
      ) : (
        <div className="border-t border-sidebar-border/60 pt-1.5 text-[10px] text-muted-foreground">
          {readout?.cursor?.onSurface ? "No selectable feature here" : "Point at the model"}
        </div>
      )}
    </div>
  );
}

export default function CursorInspectorPanel({ readout, selectMode, viewportFrameInsets, onCopyStatus, pinToken = 0 }) {
  const [collapsed, setCollapsed] = useState(false);
  const [snapshots, setSnapshots] = useState([]);
  const timersRef = useRef(new Map());
  const idRef = useRef(0);
  const readoutRef = useRef(readout);
  readoutRef.current = readout;
  const lastPinTokenRef = useRef(pinToken);

  const clearTimer = useCallback((id) => {
    const timer = timersRef.current.get(id);
    if (timer) {
      window.clearTimeout(timer);
      timersRef.current.delete(id);
    }
  }, []);

  const removeSnapshot = useCallback((id) => {
    clearTimer(id);
    setSnapshots((prev) => prev.filter((snapshot) => snapshot.id !== id));
  }, [clearTimer]);

  useEffect(() => () => {
    for (const timer of timersRef.current.values()) {
      window.clearTimeout(timer);
    }
    timersRef.current.clear();
  }, []);

  const pinReadout = useCallback((target) => {
    if (!target?.entity) {
      return;
    }
    idRef.current += 1;
    const id = idRef.current;
    setSnapshots((prev) => {
      const next = [...prev, { id, readout: target }];
      while (next.length > MAX_SNAPSHOTS) {
        clearTimer(next.shift().id);
      }
      return next;
    });
    timersRef.current.set(id, window.setTimeout(() => removeSnapshot(id), SNAPSHOT_TTL_MS));
  }, [clearTimer, removeSnapshot]);

  // A viewport click on the inspected feature bumps pinToken; freeze the current readout.
  useEffect(() => {
    if (pinToken === lastPinTokenRef.current) {
      return;
    }
    lastPinTokenRef.current = pinToken;
    pinReadout(readoutRef.current);
  }, [pinToken, pinReadout]);

  const copy = useCallback(async (text, message) => {
    try {
      await copyTextToClipboard(text);
      onCopyStatus?.(message);
    } catch (err) {
      onCopyStatus?.(err instanceof Error ? err.message : "Clipboard write failed");
    }
  }, [onCopyStatus]);

  const left = `calc(${Math.max(Number(viewportFrameInsets?.left) || 0, 0)}px + 14px)`;
  const top = `calc(${Math.max(Number(viewportFrameInsets?.top) || 0, 0)}px + 14px)`;

  return (
    <div
      className={cn("pointer-events-auto absolute z-20 w-60 overflow-hidden rounded-md text-[11px]", SURFACE_CLASS)}
      style={{ left, top }}
    >
      <div className="flex items-center justify-between gap-2 px-2.5 py-1.5">
        <span className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
          Inspect · {selectMode === "part" ? "Part" : "Feature"}
        </span>
        <button
          type="button"
          aria-label={collapsed ? "Expand inspector" : "Collapse inspector"}
          className="rounded p-0.5 text-muted-foreground hover:text-sidebar-foreground"
          onClick={() => setCollapsed((value) => !value)}
        >
          {collapsed ? <ChevronDown className="size-3.5" /> : <ChevronUp className="size-3.5" />}
        </button>
      </div>

      {collapsed ? null : (
        <div className="space-y-2 px-2.5 pb-2.5">
          <button
            type="button"
            disabled={!readout?.entity}
            onClick={() => pinReadout(readout)}
            className="block w-full rounded border border-sidebar-border/60 bg-sidebar/40 p-2 text-left transition-colors hover:bg-sidebar-accent/40 disabled:cursor-default disabled:hover:bg-sidebar/40"
            title={readout?.entity ? "Click to pin a snapshot" : undefined}
          >
            <ReadoutBody readout={readout} />
            {readout?.entity ? (
              <div className="mt-1.5 flex items-center gap-1 text-[10px] text-muted-foreground">
                <Pin className="size-3" /> Click to pin
              </div>
            ) : null}
          </button>

          {snapshots.length ? (
            <div className="space-y-1.5">
              {snapshots.map((snapshot) => (
                <div
                  key={snapshot.id}
                  className="animate-in fade-in slide-in-from-top-1 rounded border border-sidebar-border/60 bg-sidebar/30 p-2 duration-200"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate font-medium">{snapshot.readout.entity?.label}</span>
                    <button
                      type="button"
                      aria-label="Dismiss snapshot"
                      className="shrink-0 text-muted-foreground hover:text-sidebar-foreground"
                      onClick={() => removeSnapshot(snapshot.id)}
                    >
                      ×
                    </button>
                  </div>
                  <div className="truncate font-mono text-[10px] text-muted-foreground">
                    {inspectorReadoutRefToken(snapshot.readout)}
                  </div>
                  <div className="mt-1.5 flex gap-1.5">
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      className="h-6 flex-1 px-2 text-[10px]"
                      onClick={() => copy(inspectorReadoutRefToken(snapshot.readout), "Copied ref")}
                    >
                      <Copy className="size-3" /> Copy
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      className="h-6 flex-1 px-2 text-[10px]"
                      onClick={() => copy(serializeInspectorReadout(snapshot.readout), "Copied details")}
                    >
                      Copy all
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
