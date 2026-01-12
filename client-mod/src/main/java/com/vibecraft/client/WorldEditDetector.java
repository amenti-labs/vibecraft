package com.vibecraft.client;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.tree.CommandNode;
import net.minecraft.client.network.ClientPlayNetworkHandler;

import java.util.Locale;

final class WorldEditDetector {
    private WorldEditDetector() {
    }

    static boolean isWorldEditAvailable(ClientPlayNetworkHandler handler) {
        if (handler == null) {
            return false;
        }
        CommandDispatcher<?> dispatcher = handler.getCommandDispatcher();
        if (dispatcher == null) {
            return false;
        }
        CommandNode<?> root = dispatcher.getRoot();
        if (root == null) {
            return false;
        }
        for (CommandNode<?> child : root.getChildren()) {
            if (child == null) {
                continue;
            }
            String name = child.getName();
            if (name == null) {
                continue;
            }
            String normalized = name.toLowerCase(Locale.ROOT);
            if (isWorldEditRoot(normalized)) {
                return true;
            }
        }
        return false;
    }

    private static boolean isWorldEditRoot(String normalized) {
        if (normalized.startsWith("//")) {
            return true;
        }
        return normalized.equals("worldedit")
                || normalized.equals("we")
                || normalized.equals("wand")
                || normalized.equals("pos1")
                || normalized.equals("pos2")
                || normalized.equals("hpos1")
                || normalized.equals("hpos2")
                || normalized.equals("sel")
                || normalized.equals("brush")
                || normalized.equals("br");
    }
}
